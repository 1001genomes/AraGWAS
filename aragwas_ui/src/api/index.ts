import ApiVersion from '../models/apiversion';
import Page from '../models/page';
import Study from '../models/study';


// TODO convert to Typescript
function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response;
  } else {
    const error = new Error(response.statusText);
    throw error;
  }
}

// TODO convert to Typescript
function convertToModel(response) {
    return response.json();
}
// Study list
export async function loadStudies(page= 1, ordering= '') {
    return fetch(`/api/studies/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single study information
export async  function loadStudy(studyId= '1') {
    return fetch(`/api/studies/${studyId}`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfStudy(studyId= '1', page= 1, ordering= '-pvalue') {
    return fetch(`/api/associations_of_study/${studyId}/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}
// Load associations for manhattan plots
export async  function loadAssociationsForManhattan(studyId= '1') {
    return fetch(`/api/associations_manhattan/${studyId}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Phenotype list
export async  function loadPhenotypes(page = 1, ordering= '') {
    return fetch(`/api/phenotype/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single phenotype information
export async  function loadPhenotype(phenotypeId = '1') {
    return fetch(`/api/phenotype/${phenotypeId}`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfPhenotype(phenotypeId= '1', page= 1, ordering= '-pvalue') {
    return fetch(`/api/associations_of_phenotype/${phenotypeId}/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Gene list
export async  function loadGenes(page = 1, ordering= '') {
    return fetch(`/api/gene/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single gene information
export async  function loadGene(geneId = '1') {
    return fetch(`/api/gene/${geneId}`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfGene(geneId= '1', page= 1, ordering= '-pvalue') {
    return fetch(`/api/associations_of_gene/${geneId}/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}


// TODO: add strategy to store / quickly retreive top associations across all studies
export async function loadTopAssociations() {
    return fetch(`/api/top_associations/`)
        .then(checkStatus)
        .then(convertToModel);
}

export async function search(queryTerm= '', page= 1, ordering= '') {
    if (queryTerm === '') {
        return fetch(`/api/search/search_results/?page=${page}&ordering=${ordering}`)
            .then(checkStatus)
            .then(convertToModel);
    } else {
        return fetch(`/api/search/search_results/${queryTerm}/?page=${page}&ordering=${ordering}`)
            .then(checkStatus)
            .then(convertToModel);
    }

}
export async  function loadApiVersion(): Promise<ApiVersion> {
    return fetch('/api/version/')
        .then(checkStatus)
        .then(convertToModel);
}
