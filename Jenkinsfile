pipeline {
  agent any

  tools {
    git 'Default'   // use the configured Git installation name
  }
  
  options {
    timestamps()
    durabilityHint('PERFORMANCE_OPTIMIZED')
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  environment {
    VENV = ".venv"
    PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
    DJANGO_SETTINGS_MODULE = "settings.ci"   // <-- update "project"
    PYTEST_JUNIT = "reports/junit.xml"
    COVERAGE_XML = "reports/coverage.xml"

    // Flush Python output immediately to Console Output
    PYTHONUNBUFFERED = "1"

    // Oracle Instant Client location on the agent
    ORACLE_HOME     = "/opt/oracle-db-21c"
    LD_LIBRARY_PATH = "/opt/oracle-db-21c"
    PATH            = "/opt/oracle-db-21c:${PATH}"
  }

  parameters {
    choice(name: 'TARGET_ENV', choices: ['', 'dev', 'test', 'uat', 'prod'], description: 'Optional deploy target')
    booleanParam(name: 'RUN_MIGRATIONS', defaultValue: true, description: 'Run manage.py migrate')
  }

  stages {
    stage('Build') {
      steps {
        ansiColor('xterm') {
          sh '''
            set -euxo pipefail
            echo "Hello with colors"
          '''
        }
      }
    }

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Validate') {
        steps {
            script {
                sh 'ls -la'
            }
        }
    }

    stage('Set up Python') {
      steps {
        sh '''
          set -euxo pipefail
          python3 -m venv "${VENV}"
          . "${VENV}/bin/activate"
          python -m pip install --upgrade pip wheel
          mkdir -p "${PIP_CACHE_DIR}" reports logs
          pip install --cache-dir "${PIP_CACHE_DIR}" -r requirements.txt
          pip install --cache-dir "${PIP_CACHE_DIR}" pytest pytest-cov pytest-django coverage ruff
          pip list | tee logs/pip-list.txt
        '''
      }
    }

    stage('Lint') {
      steps {
        sh '''
          set -euxo pipefail
          . "${VENV}/bin/activate"
          ruff --version
          ruff check . | tee logs/ruff.txt
        '''
      }
      post {
        always {
          sh 'set -euxo pipefail; [ -f logs/ruff.txt ] && tail -n +1 logs/ruff.txt || true'
        }
      }
    }

    /*
    stage('Django sanity') {
      steps {
        sh '''
          set -euxo pipefail
          . "${VENV}/bin/activate"
          python manage.py check --deploy --settings=${DJANGO_SETTINGS_MODULE} | tee logs/django-check.txt
          python manage.py makemigrations --check --dry-run --settings=${DJANGO_SETTINGS_MODULE} | tee logs/makemigrations-check.txt
        '''
      }
      post {
        always {
          sh '''
            set -euxo pipefail
            [ -f logs/django-check.txt ] && tail -n +1 logs/django-check.txt || true
            [ -f logs/makemigrations-check.txt ] && tail -n +1 logs/makemigrations-check.txt || true
          '''
        }
      }
    }
    */

    stage('Unit Tests (Oracle)') {
      /* environment {
        // Bind Jenkins credentials into env vars for Django settings.ci
      } */
      steps {
        withCredentials([
          usernamePassword(credentialsId: 'ORACLE_DB_CREDS', usernameVariable: 'ORA_USER', passwordVariable: 'ORA_PASSWORD'),
          string(credentialsId: 'ORA_HOST', variable: 'ORA_HOST'),
          string(credentialsId: 'ORA_PORT', variable: 'ORA_PORT'),
          string(credentialsId: 'ORA_SERVICE', variable: 'ORA_SERVICE'),
          string(credentialsId: 'DJANGO_SECRET_KEY', variable: 'DJANGO_SECRET_KEY')
        ]) {
          sh '''
            set -euxo pipefail
            . "${VENV}/bin/activate"

            # Smoke test Oracle connectivity (prints to console)
            python - <<'PY'
import os, oracledb
dsn = f"{os.environ['ORA_HOST']}:{os.environ['ORA_PORT']}/{os.environ['ORA_SERVICE']}"
print("Connecting to:", dsn)
conn = oracledb.connect(user=os.environ['ORA_USER'], password=os.environ['ORA_PASSWORD'], dsn=dsn)
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM dual")
    print("Oracle ping:", cur.fetchone())
conn.close()
PY

            # Run tests with verbose streaming output
            pytest -v -s \
              --ds="${DJANGO_SETTINGS_MODULE}" \
              --junitxml="${PYTEST_JUNIT}" \
              --cov=. --cov-report=xml:"${COVERAGE_XML}" --cov-report=term
          '''
        }
      }
      /*
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/junit.xml'
          recordCoverage tools: [[parser: 'PYTHON', pattern: 'reports/coverage.xml']]
          archiveArtifacts artifacts: 'reports/**,logs/**', onlyIfSuccessful: false
        }
      }*/
    }

    stage('Migrate (optional)') {
      when { expression { return params.RUN_MIGRATIONS } }
      steps {
        withCredentials([
          usernamePassword(credentialsId: 'ORACLE_DB_CREDS', usernameVariable: 'ORA_USER', passwordVariable: 'ORA_PASSWORD'),
          string(credentialsId: 'ORA_HOST', variable: 'ORA_HOST'),
          string(credentialsId: 'ORA_PORT', variable: 'ORA_PORT'),
          string(credentialsId: 'ORA_SERVICE', variable: 'ORA_SERVICE'),
        ]) {
          sh '''
            set -euxo pipefail
            . "${VENV}/bin/activate"
            python manage.py migrate --noinput --settings=${DJANGO_SETTINGS_MODULE} | tee logs/migrate.txt
          '''
        }
      }
      post {
        always {
          sh 'set -euxo pipefail; [ -f logs/migrate.txt ] && tail -n +1 logs/migrate.txt || true'
        }
      }
    }
  }

  post {
    success { echo '✅ CI passed (Django + Oracle) with verbose console logs' }
    failure { echo '❌ CI failed — see Console Output for fully streamed logs' }
    always  { archiveArtifacts artifacts: 'logs/**', onlyIfSuccessful: false }
  }
}
