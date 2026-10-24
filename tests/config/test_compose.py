"""Valida os Composes reais sem iniciar containers ou ler credenciais locais."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def render(tmp_path):
    if not shutil.which('docker'):
        pytest.skip('Docker Compose não instalado')
    environment = {'PATH': os.environ['PATH'], 'HOME': os.environ['HOME']}
    version = subprocess.run(['docker', 'compose', 'version'], env=environment, capture_output=True)
    if version.returncode:
        pytest.skip('Docker Compose não instalado')
    config = tmp_path / '.env'
    config.write_text('DB_USER=teste\nDB_PASSWORD=senha-ficticia\nDB_NAME=teste\n'
                      'MYSQL_ROOT_PASSWORD=senha-ficticia\nIMAGE_TAG=a1ce0cf\n'
                      'MYSQL_VOLUME_NAME=gestaolegal_mysql_data\n'
                      'UPLOADS_VOLUME_NAME=gestaolegal_uploads\nDB_PORT=3336\n')

    def run(file, *args):
        result = subprocess.run(['docker', 'compose', '--project-directory', str(tmp_path),
                                 '--env-file', str(config), '-f', str(ROOT / file),
                                 *args, 'config', '--format', 'json'],
                                env=environment, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)
    return run


def test_implantacao_usa_imagens_volumes_externos_e_migracao(render):
    model = render('docker-compose.yml', '--profile', '*')
    services = model['services']
    for name in ('api', 'web', 'migrate'):
        assert services[name]['image'].endswith(':a1ce0cf')
        assert 'build' not in services[name]
    assert services['api']['environment']['DB_HOST'] == 'db'
    assert services['api']['environment']['DB_PORT'] == '3306'
    assert services['api']['depends_on']['migrate']['condition'] == 'service_completed_successfully'
    assert model['volumes']['mysql_data']['name'] == 'gestaolegal_mysql_data'
    assert model['volumes']['uploads']['name'] == 'gestaolegal_uploads'
    for volume in model['volumes'].values():
        assert volume['external'] is True
    for service in services.values():
        assert all(v['type'] == 'volume' for v in service.get('volumes', []))
        assert all(p['host_ip'] == '127.0.0.1' for p in service.get('ports', []))
    assert services['mailpit']['profiles'] == ['mailpit']
    assert services['adminer']['profiles'] == ['adminer']


def test_desenvolvimento_independente_com_mailpit_e_fontes(render):
    model = render('docker-compose.dev.yml')
    services = model['services']
    assert set(services) == {'api', 'web', 'migrate', 'db', 'mailpit'}
    for name in ('api', 'web', 'migrate'):
        assert services[name]['build']['target'] == 'dev'
    assert services['api']['environment']['FLASK_ENV'] == 'development'
    assert services['api']['environment']['MAIL_SERVER'] == 'mailpit'
    assert services['api']['environment']['DB_PORT'] == '3306'
    assert 'mailpit' in services['api']['depends_on']
    assert any(v['target'] == '/code/migrations' for v in services['migrate']['volumes'])
    assert all(not v.get('external') for v in model['volumes'].values())
