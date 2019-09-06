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
                        sh """
                        cd aragwas_ui
                        ln -s /srv/aragwas_ui/node_modules/ || true
                        npm run build
                        rm node_modules
                        """
                    }
                    //ui_img.run('-a -v $WORKSPACE/dist:/srv/aragwas_server/gwasdb')
                    //sh 'cp -r dist/* $WORKSPACE/aragwas_server/gwasdb/'
                    //FIXME this in try-catch and clean shutdown of db_cont
                    def app_img = docker.build("aragwas","aragwas_server")

                    // link app container to db container, expose platinum test config path
                    app_img.inside() {
                        // run the behave tests
                        echo "running tests"
                        sh returnStatus: true, script: "cd /srv/web/ && py.test -ra -p no:cacheprovider --junitxml ${env.WORKSPACE}/TESTS-aragwas.xml"
                    }
                     // collect unit test results
                    junit "TESTS-aragwas.xml"
                }
            }
        }

        // not _really_ deploy, but push to local registry
        stage('deploy') {
            when{
                branch 'master'
            }
            steps {
                script {
                    sh 'sh write_version.sh'
                    //FIXME leaking local infra details
                    docker.withRegistry('https://docker.artifactory.imp.ac.at', 'jenkins_artifactory_creds') {

                        // push DB docker img to registry
                        def server_img = docker.build("docker.artifactory.imp.ac.at/the1001genomes/aragwas", "aragwas_server")

                        server_img.push('latest')
                        sshagent(['1001genome_deploy_ssh_key']) {
                            env.DEPLOY_HOST = 'aragwas.sci.gmi.oeaw.ac.at'
                            sh '''
                                scp -o StrictHostKeyChecking=no aragwas_server/docker-compose.yml root@$DEPLOY_HOST:/root/
                                ssh -o StrictHostKeyChecking=no root@$DEPLOY_HOST "cd /root && docker-compose pull && docker-compose up -d"
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
        // always {
        //     // notify build results, see https://jenkins.io/blog/2016/07/18/pipline-notifications/
        //     // notifyBuild(currentBuild.result)

        // }
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
