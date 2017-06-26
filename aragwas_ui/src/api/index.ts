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

// Cross-website request to access data on arapheno
// function createCORSRequest(method, url) {
//     let xhr = new XMLHttpRequest();
//     let XDomainRequest;
//     if ("withCredentials" in xhr) {
//
//         // Check if the XMLHttpRequest object has a "withCredentials" property.
//         // "withCredentials" only exists on XMLHTTPRequest2 objects.
//         xhr.open(method, url, true);
//
//     } else if (typeof XDomainRequest != "undefined") {
//
//         // Otherwise, check if XDomainRequest.
//         // XDomainRequest only exists in IE, and is IE's way of making CORS requests.
//         xhr = new XDomainRequest();
//         xhr.open(method, url);
//
//     } else {
//
//         // Otherwise, CORS is not supported by the browser.
//         xhr = null;
//
//     }
//     return xhr;
// }

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
export async  function loadAggregatedStatisticsOfStudy(studyId: number, filter) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    let url = `/api/studies/${studyId}/aggregated_statistics/?`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
// Load associations for manhattan plots
export async  function loadAssociationsForManhattan(studyId: number) {
    return fetch(`/api/studies/${studyId}/gwas/?filter=5000&filter_type=top`)
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
export async  function loadAggregatedStatisticsOfPhenotype(phenotypeId: number, filter) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    let url = `/api/phenotypes/${phenotypeId}/aggregated_statistics/?`;
    if (queryParam) {
        url += "?" + queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
// Load similar phenotypes based on ontology
export async function loadSimilarPhenotypes(phenotypeId: number) {
    const arapheno = fetch(`https://arapheno.1001genomes.org:443/rest/phenotype/`+phenotypeId+`.json`)
        .then(checkStatus)
        .then(convertToModel);
    const to_term = arapheno["to_term"];
    const search_res = fetch(`https://arapheno.1001genomes.org:443/rest/search/`+to_term+`.json`)
        .then(checkStatus)
        .then(convertToModel);
    return search_res["phenotype_search_results"];
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
    let url = `/api/genes/${geneId}/associations/?limit=25&offset=${offset}&zoom=${zoom}`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAggregatedStatisticsOfGene(geneId = "1", zoom: number, filter) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    let url = `/api/genes/${geneId}/aggregated_statistics/?zoom=${zoom}`;
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
export async function loadTopAssociations(filter, page, lastElement = [0,'']) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = 25 * ( page - 1);
    let url = `/api/associations/`;
    if (lastElement[0] !== 0) {
        url += '?lastel=' + lastElement[0].toString() + ',' + lastElement[1]
    } else {
        url += `?limit=25&offset=${offset}`
    }
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadTopAggregatedStatistics(filter) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    let url = `/api/associations/aggregated_statistics/?`;
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
export async  function loadSnpStatistics() {
    return fetch(`/api/snps/aggregated/`)
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
