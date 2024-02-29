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
    pushRegistryNamespace: "the1001genomes",
    imageName: "aragwas-backend",
    pushBranches: ['master', 'fix_mail'],
    test: testScript('py.test -ra -p no:cacheprovider /srv/web --junitxml junit.xml', '**/junit.xml'),
    containerImages: extraImages,
    tower: jobsMapping
])