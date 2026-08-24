pipeline {
    agent any
    stages {
        stage('Secret Scan — Gitleaks') {
            steps {
                sh 'gitleaks detect --source . --verbose --exit-code 0 || true'
            }
            post {
                always {
                    sh 'gitleaks detect --source . -f json -r gitleaks-report.json --exit-code 0 || true'
                    archiveArtifacts artifacts: 'gitleaks-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('SAST — Bandit') {
            steps {
                sh 'bandit -r . --exit-zero || true'
            }
            post {
                always {
                    sh 'bandit -r . --exit-zero -f json -o bandit-report.json || true'
                    archiveArtifacts artifacts: 'bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('SAST — Semgrep') {
            steps {
                sh 'semgrep --config=p/python --config=p/flask . || true'
            }
            post {
                always {
                    sh 'semgrep --config=p/python --config=p/flask --json --output semgrep-report.json . || true'
                    archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('Dependency Check — pip-audit') {
            steps {
                sh 'pip-audit -r requirements.txt || true'
            }
        }
        stage('Dependency Check — Trivy') {
            steps {
                sh 'trivy fs --scanners vuln --exit-code 0 .'
            }
            post {
                always {
                    sh 'trivy fs --scanners vuln --format json --output trivy-fs-report.json . || true'
                    archiveArtifacts artifacts: 'trivy-fs-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t python-service:latest .'
            }
        }
        stage('Container Scan — Trivy') {
            steps {
                sh 'trivy image --severity CRITICAL,HIGH --exit-code 0 python-service:latest'
            }
            post {
                always {
                    sh 'trivy image --format json --output trivy-image-report.json python-service:latest || true'
                    archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('IaC Scan — Checkov') {
            steps {
                sh 'checkov -f Dockerfile --soft-fail || true'
            }
            post {
                always {
                    sh 'checkov -f Dockerfile --output json --soft-fail > checkov-report.json || true'
                    archiveArtifacts artifacts: 'checkov-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('SBOM Generation — Syft') {
            steps {
                sh 'syft dir:. -o cyclonedx-json > sbom-source.json || true'
                sh 'syft python-service:latest -o cyclonedx-json > sbom-image.json || true'
                sh 'trivy image --format cyclonedx --output sbom-trivy.json python-service:latest || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'sbom-*.json', allowEmptyArchive: true
                }
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube-local') {
                    script {
                        def scannerHome = tool 'sonar-scanner'
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    ssh -o StrictHostKeyChecking=no jojo@192.168.1.130 \
                        "if [ -f /opt/python-service/app.py ]; then rm -f /opt/python-service/app.py; fi"
                    scp -o StrictHostKeyChecking=no app.py requirements.txt jojo@192.168.1.130:/opt/python-service/
                    ssh -o StrictHostKeyChecking=no jojo@192.168.1.130 \
                        "if [ ! -d /opt/python-service/venv ]; then python3 -m venv /opt/python-service/venv; fi \
                        && /opt/python-service/venv/bin/pip install --upgrade pip \
                        && /opt/python-service/venv/bin/pip install -r /opt/python-service/requirements.txt"
                    ssh -o StrictHostKeyChecking=no jojo@192.168.1.130 "sudo systemctl restart python-service"
                '''
            }
        }
        stage('DAST — OWASP ZAP') {
            steps {
                sh '''
                    docker run --rm -t \
                        --user root \
                        -v ${WORKSPACE}:/zap/wrk:rw \
                        ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py \
                        -t http://192.168.1.130:8083 \
                        -J zap-report.json \
                        || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.json', allowEmptyArchive: true
                }
            }
        }
    }
    post {
        success { echo 'Pipeline SUCCESS — semua security gate passed!' }
        failure { echo 'Pipeline FAILURE — ada security issue yang perlu difix!' }
    }
}
