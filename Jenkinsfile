@Library('vbc-cicd@docker_multi_test')
def jobsMapping = [
  tags: [jobName:"App AraGWAS", jobTags: "reload", extraVars: "app_generic_image_tag: latest"],
  master: [jobName:"App AraGWAS", jobTags: "reload", extraVars: "app_generic_image_tag: master"]
]

def extraImages =
[
    [imageName: "aragwas-backend", dockerFile: "Dockerfile", dockerContext: ".", extraBuildArgs: '--target aragwas-backend'],
    [imageName: "aragwas-worker", test: null, dockerFile: "Dockerfile", dockerContext: ".", extraBuildArgs: '--target aragwas-worker']
]

buildDockerImage([
    //imageName: "aragwas-backend",
    pushRegistryNamespace: "the1001genomes",
    pushBranches: ['develop', 'master'],
    test: testScript('py.test -ra -p no:cacheprovider /srv/web --junitxml junit.xml', '**/junit.xml'),
    containerImages: extraImages
    //tower: jobsMapping
])