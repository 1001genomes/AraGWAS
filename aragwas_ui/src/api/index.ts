import ApiVersion from "../models/apiversion";
import Gene from "../models/gene";
import Page from "../models/page";
import Study from "../models/study";

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
function convertToModel<T>(response): T {
    return response.json();
}

function getTopAssociationsParametersQuery(filter): string {
    let queryParam: string = "";
    for (const key of Object.keys(filter)) {
        let filterParam = "";
        for (let i = 0; i < filter[key].length; i++) {
            const val = filter[key][i];
            if (i > 0) {
                filterParam += "&";
            }
            filterParam += `${key}=${val}`;
        }
        queryParam += "&" + filterParam;
    }
    return queryParam;
}

// Study list
export async function loadStudies(page: number = 1, ordering = "") {
    return fetch(`/api/studies/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single study information
export async  function loadStudy(studyId: number) {
    return fetch(`/api/studies/${studyId}`)
        .then(checkStatus)
        .then(convertToModel);
}
// Load top genes and snp type identified for this study
export async  function loadStudyTopHits(studyId: number) {
    return fetch(`/api/studies/${studyId}/top/`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfStudy(studyId: number, filter, page= 1) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = 25 * (page - 1);
    let url = `/api/studies/${studyId}/associations/?limit=25&offset=${offset}`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
// Load associations for manhattan plots
export async  function loadAssociationsForManhattan(studyId: number) {
    return fetch(`/api/studies/${studyId}/gwas/?filter=2500&filter_type=top`)
        .then(checkStatus)
        .then(convertToModel);
}

// Phenotype list
export async  function loadPhenotypes(page: number = 1, ordering= "") {
    return fetch(`/api/phenotypes/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single phenotype information
export async  function loadPhenotype(phenotypeId: number) {
    return fetch(`/api/phenotypes/${phenotypeId}`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfPhenotype(phenotypeId: number, filter,  page: number= 1) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = 25 * ( page - 1);
    let url = `/api/phenotypes/${phenotypeId}/associations/?limit=25&offset=${offset}`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
// Load similar phenotypes based on ontology
export async function loadSimilarPhenotypes(phenotypeId: number) {
    return fetch(`/api/phenotypes/${phenotypeId}/similar/`)
        .then(checkStatus)
        .then(convertToModel);
}
export async function loadStudiesOfPhenotype(phenotypeId: number) {
    return fetch(`/api/phenotypes/${phenotypeId}/studies/`)
        .then(checkStatus)
        .then(convertToModel);
}


// Gene list
export async function loadGenes(page: number = 1, ordering= "") {
    return fetch(`/api/genes/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single gene information
export async function loadGene(geneId = ""): Promise<Gene> {
    return fetch(`/api/genes/${geneId}`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfGene(geneId= "1", zoom: number, filter, page: number = 1) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = 25 * (page - 1);
    let url = `/api//genes/${geneId}/associations/?limit=25&offset=${offset}zoom=${zoom}`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}

export async function loadTopAssociations(filter, page) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = 25 * ( page - 1);
    let url = `/api/associations/?limit=25&offset=${offset}`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadTopGenes() {
    return fetch(`/api/genes/top/`)
        .then(checkStatus)
        .then(convertToModel);
}
export async function loadAssociationCount() {
    return fetch(`/api/associations/count/`)
        .then(checkStatus)
        .then(convertToModel);
}

export async function search(queryTerm= "", page: number = 1, ordering= "") {
    if (queryTerm === "") {
        return fetch(`/api/search/search_results/?page=${page}&ordering=${ordering}`)
            .then(checkStatus)
            .then(convertToModel);
    } else {
        return fetch(`/api/search/search_results/${queryTerm}/?page=${page}&ordering=${ordering}`)
            .then(checkStatus)
            .then(convertToModel);
    }
}

export async function autoCompleteGenes(queryTerm: string): Promise<Gene[]> {
    return fetch(`/api/genes/autocomplete/?term=${queryTerm}`)
        .then(checkStatus)
        .then(convertToModel);
}

export async  function loadApiVersion(): Promise<ApiVersion> {
    return fetch("/api/version/")
        .then(checkStatus)
        .then(convertToModel);
}
