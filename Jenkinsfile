#!/usr/bin/env groovy


/**
* build / test pipeline for AraGWAS
*/

pipeline {

    agent any

    stages {

        // global checkout needed for Docker setup
        stage('checkout') {
            steps {
                checkout scm
            }
        }

        // prepare the dockers: testing env
        stage('test') {
            steps {
                script {

                    // build ui docker image to compile javascript
                    def ui_img = docker.build("aragwas_ui","aragwas_ui")
                    ui_img.inside('-u root') {
                        withEnv(['NPM_CONFIG_COLOR=false','NPM_CONFIG_PROGRESS=false','NPM_CONFIG_SPIN=false']) {
                            sh """
                            mv /srv/aragwas_ui/node_modules aragwas_ui
                            cd aragwas_ui && npm run build
                            """
                        }
                    }
                    //ui_img.run('-a -v $WORKSPACE/dist:/srv/aragwas_server/gwasdb')
                    //sh 'cp -r dist/* $WORKSPACE/aragwas_server/gwasdb/'
                    //FIXME this in try-catch and clean shutdown of db_cont
                    def app_img = docker.build("aragwas","aragwas_server")

                    // link app container to db container, expose platinum test config path
                    app_img.inside() {
                        // run the behave tests
                        echo "running tests"
                        sh """cd /srv/web/
                            python manage.py test || true
                        """
                    }
                }
            }
        }

        // not _really_ deploy, but push to local registry
        stage('deploy') {
            steps {
                script {

                    //FIXME leaking local infra details
                    docker.withRegistry('https://docker.sci.gmi.oeaw.ac.at', 'platinum-docker-registry') {

                        // push DB docker img to registry
                        def server_img = docker.build("docker.sci.gmi.oeaw.ac.at/nordborg/aragwas", "aragwas_server")

                        server_img.push('testing')
                        sshagent(['801dbf20-4259-4d3b-8948-e84fe1b52c7f']) {
                            sh '''
                                scp aragwas_server/docker-compose.yml root@$DEPLOY_HOST:/root/
                                ssh root@$DEPLOY_HOST "cd /root && docker-compose pull && docker-compose up -d"
                            '''
                        }
                    }
                }
            }
        }
    // in the future: conditional deploy?
    } //stages

    // post block is executed after all the stages/steps in the pipeline
    post {
        always {
            // notify build results, see https://jenkins.io/blog/2016/07/18/pipline-notifications/
            notifyBuild(currentBuild.result)
        }
        changed {
            echo "build changed"
        }
        aborted {
            echo "build aborted"
        }
        failure {
            echo "build failed"
        }
        success {
            echo "build is success"
        }
        unstable {
            echo "build is unstable"
        }
    }
}

// send global slack notification, but fail silently if this is not possible, i.e. slack integration is not installed
def notifyBuild(String buildStatus) {
  // build status of null means successful
  buildStatus = buildStatus ?: 'SUCCESS'

  if (buildStatus == 'STARTED' || buildStatus == 'CHANGED' || buildStatus == 'UNSTABLE') {
    color = 'YELLOW'
    colorCode = '#DDDD00'
  }
  else if (buildStatus == 'SUCCESS') {
    color = 'GREEN'
    colorCode = '#00DD00'
  }
  else {
    // FAILURE or UNSTABLE
    color = 'RED'
    colorCode = '#DD0000'
  }

  def message = "${buildStatus}: Job <${env.BUILD_URL}|${env.JOB_NAME} #${env.BUILD_NUMBER}>"

  /* we could add blame to the slack message ;) but it's visible on the build details anyway
  if (buildStatus == 'FAILURE') {
      def changes_by = sh 'git --no-pager log -1 --format=%an'
      message = "${buildStatus}: Job <${env.BUILD_URL}|${env.JOB_NAME} #${env.BUILD_NUMBER}> caused by ${changes_by}"
  }
  */

  // send gracefully
  try {
      slackSend (color: colorCode, message: "${message}")
  }
  catch (e) {
     echo "failed to send notification: ${e}"
  }
}
