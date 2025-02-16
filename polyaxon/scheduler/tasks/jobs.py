import logging

from polystores.exceptions import PolyaxonStoresException

import conf
import workers

from db.getters.jobs import get_valid_job
from db.redis.heartbeat import RedisHeartBeat
from lifecycles.jobs import JobLifeCycle
from logs_handlers.collectors import logs_collect_job
from options.registry.scheduler import SCHEDULER_GLOBAL_COUNTDOWN_DELAYED
from polyaxon.settings import Intervals, SchedulerCeleryTasks
from scheduler import dockerizer_scheduler, job_scheduler
from stores.exceptions import VolumeNotFoundError

_logger = logging.getLogger(__name__)


@workers.app.task(name=SchedulerCeleryTasks.JOBS_BUILD, ignore_result=True)
def jobs_build(job_id):
    job = get_valid_job(job_id=job_id)
    if not job:
        return None

    if not JobLifeCycle.can_transition(status_from=job.last_status,
                                       status_to=JobLifeCycle.BUILDING):
        _logger.info('Job id `%s` cannot transition from `%s` to `%s`.',
                     job_id, job.last_status, JobLifeCycle.BUILDING)
        return

    build_job, image_exists, build_status = dockerizer_scheduler.create_build_job(
        user=job.user,
        project=job.project,
        config=job.specification.build,
        config_map_refs=job.config_map_refs,
        secret_refs=job.secret_refs,
        code_reference=job.code_reference)

    job.build_job = build_job
    job.save(update_fields=['build_job'])
    if image_exists:
        # The image already exists, so we can start the experiment right away
        workers.send(
            SchedulerCeleryTasks.JOBS_START,
            kwargs={'job_id': job_id})
        return

    if not build_status:
        job.set_status(JobLifeCycle.FAILED, message='Could not start build process.')
        return

    # Update job status to show that its building docker image
    job.set_status(JobLifeCycle.BUILDING, message='Building container')


@workers.app.task(name=SchedulerCeleryTasks.JOBS_START, ignore_result=True)
def jobs_start(job_id):
    job = get_valid_job(job_id=job_id)
    if not job:
        return None

    if job.last_status == JobLifeCycle.RUNNING:
        _logger.warning('Job is already running.')
        return None

    if not JobLifeCycle.can_transition(status_from=job.last_status,
                                       status_to=JobLifeCycle.SCHEDULED):
        _logger.info('Job `%s` cannot transition from `%s` to `%s`.',
                     job.unique_name, job.last_status, JobLifeCycle.SCHEDULED)
        return None

    job_scheduler.start_job(job)


@workers.app.task(name=SchedulerCeleryTasks.JOBS_SCHEDULE_DELETION, ignore_result=True)
def jobs_schedule_deletion(job_id, immediate=False):
    job = get_valid_job(job_id=job_id, include_deleted=True)
    if not job:
        return None

    job.archive()

    if job.is_stoppable:
        project = job.project
        workers.send(
            SchedulerCeleryTasks.JOBS_STOP,
            kwargs={
                'project_name': project.unique_name,
                'project_uuid': project.uuid.hex,
                'job_name': job.unique_name,
                'job_uuid': job.uuid.hex,
                'update_status': True,
                'collect_logs': False,
                'is_managed': job.is_managed,
                'message': 'Job is scheduled for deletion.'
            })

    if immediate:
        workers.send(
            SchedulerCeleryTasks.DELETE_ARCHIVED_JOB,
            kwargs={
                'job_id': job_id,
            },
            countdown=conf.get(SCHEDULER_GLOBAL_COUNTDOWN_DELAYED))


@workers.app.task(name=SchedulerCeleryTasks.JOBS_STOP, bind=True, max_retries=3, ignore_result=True)
def jobs_stop(self,
              project_name,
              project_uuid,
              job_name,
              job_uuid,
              update_status=True,
              collect_logs=True,
              is_managed=True,
              message=None):
    if collect_logs and is_managed:
        try:
            logs_collect_job(job_uuid=job_uuid)
        except (OSError, VolumeNotFoundError, PolyaxonStoresException):
            _logger.warning('Scheduler could not collect the logs for job `%s`.', job_name)
    if is_managed:
        deleted = job_scheduler.stop_job(
            project_name=project_name,
            project_uuid=project_uuid,
            job_name=job_name,
            job_uuid=job_uuid)
    else:
        deleted = True

    if not deleted and self.request.retries < 2:
        _logger.info('Trying again to delete job `%s`.', job_name)
        self.retry(countdown=Intervals.EXPERIMENTS_SCHEDULER)
        return

    if not update_status:
        return

    job = get_valid_job(job_uuid=job_uuid, include_deleted=True)
    if not job:
        return None

    # Update notebook status to show that its stopped
    job.set_status(status=JobLifeCycle.STOPPED,
                   message=message or 'Job was stopped.')


@workers.app.task(name=SchedulerCeleryTasks.JOBS_CHECK_HEARTBEAT, ignore_result=True)
def jobs_check_heartbeat(job_id):
    if RedisHeartBeat.job_is_alive(job_id=job_id):
        return

    job = get_valid_job(job_id=job_id)
    if not job:
        return

    # Job is zombie status
    job.set_status(JobLifeCycle.FAILED,
                   message='Job is in zombie state (no heartbeat was reported).')
