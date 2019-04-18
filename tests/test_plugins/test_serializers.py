from unittest.mock import patch

import pytest

from api.plugins.serializers import (
    NotebookJobDetailSerializer,
    NotebookJobSerializer,
    NotebookJobStatusSerializer,
    ProjectNotebookJobSerializer,
    ProjectTensorboardJobSerializer,
    TensorboardJobDetailSerializer,
    TensorboardJobSerializer,
    TensorboardJobStatusSerializer
)
from constants.jobs import JobLifeCycle
from db.models.notebooks import NotebookJob, NotebookJobStatus
from db.models.tensorboards import TensorboardJob, TensorboardJobStatus
from factories.factory_plugins import (
    NotebookJobFactory,
    NotebookJobStatusFactory,
    TensorboardJobFactory,
    TensorboardJobStatusFactory
)
from factories.factory_projects import ProjectFactory
from factories.fixtures import notebook_spec_parsed_content, tensorboard_spec_parsed_content
from tests.base.case import BaseTest


@pytest.mark.plugins_mark
class TestTensorboardJobStatusSerializer(BaseTest):
    serializer_class = TensorboardJobStatusSerializer
    model_class = TensorboardJobStatus
    factory_class = TensorboardJobStatusFactory
    expected_keys = {'id', 'uuid', 'job', 'created_at', 'status', 'traceback', 'message', 'details'}

    def setUp(self):
        super().setUp()
        with patch.object(TensorboardJob, 'set_status') as _:  # noqa
            self.obj1 = self.factory_class()
            self.obj2 = self.factory_class()

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('job') == self.obj1.job.id
        data.pop('created_at')

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.plugins_mark
class TestProjectTensorboardJobSerializer(BaseTest):
    serializer_class = ProjectTensorboardJobSerializer
    model_class = TensorboardJob
    factory_class = TensorboardJobFactory
    expected_keys = {
        'id',
        'uuid',
        'name',
        'unique_name',
        'pod_id',
        'build_job',
        'node_scheduled',
        'user',
        'description',
        'created_at',
        'updated_at',
        'started_at',
        'finished_at',
        'last_status',
        'tags',
        'project',
        'experiment_group',
        'experiment',
    }

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.obj1 = self.factory_class(project=self.project)
        self.obj2 = self.factory_class(project=self.project)

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_one_with_status(self):
        obj1 = self.factory_class(project=self.project)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is None
        assert data['finished_at'] is None

        TensorboardJobStatus.objects.create(job=obj1, status=JobLifeCycle.SCHEDULED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is None

        TensorboardJobStatus.objects.create(job=obj1, status=JobLifeCycle.SUCCEEDED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is not None

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.plugins_mark
class TestTensorboardJobDetailSerializer(BaseTest):
    serializer_class = TensorboardJobDetailSerializer
    model_class = TensorboardJob
    factory_class = TensorboardJobFactory
    expected_keys = {
        'id',
        'uuid',
        'name',
        'unique_name',
        'pod_id',
        'build_job',
        'node_scheduled',
        'user',
        'description',
        'created_at',
        'updated_at',
        'started_at',
        'finished_at',
        'last_status',
        'tags',
        'config',
        'resources',
        'node_scheduled',
        'project',
        'experiment_group',
        'experiment',
    }

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.obj1 = self.factory_class(project=self.project)
        self.obj2 = self.factory_class(project=self.project)

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_one_with_status(self):
        obj1 = self.factory_class(project=self.project)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is None
        assert data['finished_at'] is None

        TensorboardJobStatus.objects.create(job=obj1, status=JobLifeCycle.SCHEDULED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is None

        TensorboardJobStatus.objects.create(job=obj1, status=JobLifeCycle.SUCCEEDED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is not None

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.plugins_mark
class TestNotebookJobStatusSerializer(BaseTest):
    serializer_class = NotebookJobStatusSerializer
    model_class = NotebookJobStatus
    factory_class = NotebookJobStatusFactory
    expected_keys = {'id', 'uuid', 'job', 'created_at', 'status', 'traceback', 'message', 'details'}

    def setUp(self):
        super().setUp()
        with patch.object(NotebookJob, 'set_status') as _:  # noqa
            self.obj1 = self.factory_class()
            self.obj2 = self.factory_class()

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('job') == self.obj1.job.id
        data.pop('created_at')

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.plugins_mark
class TestProjectNotebookJobSerializer(BaseTest):
    serializer_class = ProjectNotebookJobSerializer
    model_class = NotebookJob
    factory_class = NotebookJobFactory
    expected_keys = {
        'id',
        'uuid',
        'name',
        'unique_name',
        'pod_id',
        'build_job',
        'node_scheduled',
        'user',
        'description',
        'created_at',
        'updated_at',
        'started_at',
        'finished_at',
        'last_status',
        'tags',
        'backend',
        'project',
    }

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.obj1 = self.factory_class(project=self.project)
        self.obj2 = self.factory_class(project=self.project)

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        assert data.pop('build_job') == (
            self.obj1.build_job.unique_name if self.obj1.build_job else None)
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_one_with_status(self):
        obj1 = self.factory_class(project=self.project)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is None
        assert data['finished_at'] is None

        NotebookJobStatus.objects.create(job=obj1, status=JobLifeCycle.SCHEDULED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is None

        NotebookJobStatus.objects.create(job=obj1, status=JobLifeCycle.SUCCEEDED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is not None

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.plugins_mark
class TestNotebookJobDetailSerializer(BaseTest):
    serializer_class = NotebookJobDetailSerializer
    model_class = NotebookJob
    factory_class = NotebookJobFactory
    expected_keys = {
        'id',
        'uuid',
        'name',
        'unique_name',
        'pod_id',
        'build_job',
        'node_scheduled',
        'user',
        'description',
        'created_at',
        'updated_at',
        'started_at',
        'finished_at',
        'last_status',
        'tags',
        'config',
        'data_refs',
        'resources',
        'node_scheduled',
        'backend',
        'project',
    }

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.obj1 = self.factory_class(project=self.project)
        self.obj2 = self.factory_class(project=self.project)

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        assert data.pop('build_job') == (
            self.obj1.build_job.unique_name if self.obj1.build_job else None)
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_one_with_status(self):
        obj1 = self.factory_class(project=self.project)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is None
        assert data['finished_at'] is None

        NotebookJobStatus.objects.create(job=obj1, status=JobLifeCycle.SCHEDULED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is None

        NotebookJobStatus.objects.create(job=obj1, status=JobLifeCycle.SUCCEEDED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is not None

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.plugins_mark
class BasePluginJobSerializerTest(BaseTest):
    model_class = None
    serializer_class = None
    factory_class = None
    content = None

    def test_validation_raises_for_invalid_data(self):
        # No data
        serializer = self.serializer_class(data={})  # pylint:disable=not-callable
        assert serializer.is_valid() is False

        # Wrong spec
        serializer = self.serializer_class(data={'config': {}})  # pylint:disable=not-callable
        assert serializer.is_valid() is False

    def test_validation_passes_for_valid_data(self):
        serializer = self.serializer_class(  # pylint:disable=not-callable
            data={'config': self.content.parsed_data})
        assert serializer.is_valid() is True

    def creating_plugin_job_from_valid_data(self):
        assert self.model_class.objects.count() == 0
        serializer = self.serializer_class(  # pylint:disable=not-callable
            data={'config': self.content.parsed_data})
        serializer.is_valid()
        serializer.save()
        assert self.model_class.objects.count() == 1

    def updating_plugin_job(self):
        obj = self.factory_class()  # pylint:disable=not-callable
        assert obj.config['version'] == 1
        config = self.content.parsed_data
        config['version'] = 2
        serializer = self.serializer_class(  # pylint:disable=not-callable
            instance=obj,
            data={'config': config})
        serializer.is_valid()
        serializer.save()
        obj.refresh_from_db()
        assert obj.config['version'] == 2


@pytest.mark.plugins_mark
class TestTensorboardJobSerializer(BaseTest):
    serializer_class = TensorboardJobSerializer
    model_class = TensorboardJob
    factory_class = TensorboardJobFactory
    content = tensorboard_spec_parsed_content


@pytest.mark.plugins_mark
class TestNotebookJobSerializer(BaseTest):
    serializer_class = NotebookJobSerializer
    model_class = NotebookJob
    factory_class = NotebookJobFactory
    content = notebook_spec_parsed_content


# Prevent this base class from running tests
del BasePluginJobSerializerTest
