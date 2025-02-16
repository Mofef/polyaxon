from typing import Dict, List, Optional, Tuple

from hestia.datetime_typing import AwareDT

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

import conf

from constants.images_tags import LATEST_IMAGE_TAG
from constants.k8s_jobs import DOCKERIZER_JOB_NAME, JOB_NAME_FORMAT
from db.models.abstract.backend import BackendModel
from db.models.abstract.deleted import DeletedModel
from db.models.abstract.describable import DescribableModel
from db.models.abstract.is_managed import IsManagedModel
from db.models.abstract.job import AbstractJobModel, AbstractJobStatusModel, JobMixin
from db.models.abstract.nameable import NameableModel
from db.models.abstract.node_scheduling import NodeSchedulingModel
from db.models.abstract.persistence import PersistenceModel
from db.models.abstract.sub_paths import SubPathModel
from db.models.abstract.tag import TagModel
from db.models.unique_names import BUILD_UNIQUE_NAME_FORMAT
from db.redis.heartbeat import RedisHeartBeat
from libs.paths.jobs import get_job_subpath
from libs.spec_validation import validate_build_spec_config
from options.registry.build_jobs import BUILD_JOBS_ALWAYS_PULL_LATEST
from schemas import BuildSpecification


class BuildJob(AbstractJobModel,
               BackendModel,
               IsManagedModel,
               NodeSchedulingModel,
               NameableModel,
               DescribableModel,
               PersistenceModel,
               SubPathModel,
               TagModel,
               DeletedModel,
               JobMixin):
    """A model that represents the configuration for build job."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='+')
    project = models.ForeignKey(
        'db.Project',
        on_delete=models.CASCADE,
        related_name='build_jobs')
    content = models.TextField(
        null=True,
        blank=True,
        help_text='The yaml content of the polyaxonfile/specification.',
        validators=[validate_build_spec_config])
    code_reference = models.ForeignKey(
        'db.CodeReference',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+')
    dockerfile = models.TextField(
        blank=True,
        null=True,
        help_text='The dockerfile used to create the image with this job.')
    status = models.OneToOneField(
        'db.BuildJobStatus',
        related_name='+',
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL)

    class Meta:
        app_label = 'db'
        unique_together = (('project', 'name'),)
        indexes = [
            models.Index(fields=['name']),
        ]

    @cached_property
    def commit(self):
        if self.code_reference:
            return self.code_reference.commit
        return None

    @cached_property
    def unique_name(self) -> str:
        return BUILD_UNIQUE_NAME_FORMAT.format(
            project_name=self.project.unique_name,
            id=self.id)

    @cached_property
    def subpath(self) -> str:
        return get_job_subpath(job_name=self.unique_name)

    @cached_property
    def build_image(self) -> str:
        return self.specification.config.image

    @cached_property
    def build_dockerfile(self) -> str:
        return self.specification.config.dockerfile

    @cached_property
    def build_context(self) -> str:
        return self.specification.config.context

    @cached_property
    def build_steps(self) -> List[str]:
        return self.specification.config.build_steps

    @cached_property
    def build_env_vars(self) -> Optional[List[str]]:
        return self.specification.config.env_vars

    @cached_property
    def build_nocache(self) -> List[str]:
        return self.specification.config.nocache

    @cached_property
    def pod_id(self) -> str:
        return JOB_NAME_FORMAT.format(name=DOCKERIZER_JOB_NAME, job_uuid=self.uuid.hex)

    @cached_property
    def specification(self) -> 'BuildSpecification':
        return BuildSpecification(values=self.content) if self.content else None

    @property
    def has_specification(self) -> bool:
        return self.content is not None

    def _ping_heartbeat(self) -> None:
        RedisHeartBeat.build_ping(self.id)

    def set_status(self,  # pylint:disable=arguments-differ
                   status: str,
                   created_at: AwareDT = None,
                   message: str = None,
                   traceback: Dict = None,
                   details: Dict = None) -> bool:
        params = {'created_at': created_at} if created_at else {}
        return self._set_status(status_model=BuildJobStatus,
                                status=status,
                                message=message,
                                traceback=traceback,
                                details=details,
                                **params)

    @staticmethod
    def create(user,
               project,
               config,
               code_reference,
               config_map_refs=None,
               secret_refs=None,
               nocache=False) -> Tuple['BuildJob', bool]:
        build_spec = BuildSpecification.create_specification(config,
                                                             configmap_refs=config_map_refs,
                                                             secret_refs=secret_refs,
                                                             to_dict=False)
        if not nocache and build_spec.config.nocache is not None:
            # Set the config's nocache rebuild
            nocache = build_spec.config.nocache
        # Check if image is not using latest tag, then we can reuse a previous build
        rebuild_cond = (
            nocache or
            (conf.get(BUILD_JOBS_ALWAYS_PULL_LATEST) and
             build_spec.config.image_tag == LATEST_IMAGE_TAG)
        )
        if not rebuild_cond:
            job = BuildJob.objects.filter(project=project,
                                          content=build_spec.raw_data,
                                          code_reference=code_reference).last()
            if job:
                return job, False

        return BuildJob.objects.create(user=user,
                                       project=project,
                                       content=build_spec.raw_data,
                                       code_reference=code_reference), True


class BuildJobStatus(AbstractJobStatusModel):
    """A model that represents build job status at certain time."""
    job = models.ForeignKey(
        'db.BuildJob',
        on_delete=models.CASCADE,
        related_name='statuses')

    class Meta(AbstractJobStatusModel.Meta):
        app_label = 'db'
        verbose_name_plural = 'Build Job Statuses'
