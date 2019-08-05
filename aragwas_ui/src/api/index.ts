import Accession from "../models/accession";
import ApiVersion from "../models/apiversion";
import Association from "../models/association";
import Gene from "../models/gene";
import KOAssociation from "../models/koassociation";
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

export function getTopAssociationsParametersQuery(filter): string {
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
export async function loadStudies(page: number = 1, ordering = ""): Promise<Study[]> {
    return fetch(`/api/studies/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then<Study[]>(convertToModel);
}

// Import single study information
export async function loadStudy(studyId: number): Promise<Study> {
    return fetch(`/api/studies/${studyId}/`)
        .then(checkStatus)
        .then<Study>(convertToModel);
}
// Load top genes and snp type identified for this study
export async function loadStudyTopHits(studyId: number) {
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
export async function loadAggregatedStatisticsOfStudy(studyId: number, filter) {
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
export async function loadAssociationsForManhattan(studyId: number) {
    return fetch(`/api/studies/${studyId}/gwas/?filter=3000&filter_type=top`)
        .then(checkStatus)
        .then(convertToModel);
}
// Load ko associations for manhattan plots
export async function loadKOAssociationsForManhattan(studyId: number) {
    return fetch(`/api/studies/${studyId}/ko_mutations/`)
        .then(checkStatus)
        .then(convertToModel);
}

// Phenotype list
export async function loadPhenotypes(page: number = 1, ordering= "") {
    return fetch(`/api/phenotypes/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}

// Import single phenotype information
export async  function loadPhenotype(phenotypeId: number) {
    return fetch(`/api/phenotypes/${phenotypeId}/`)
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
    // return fetch(`http://localhost:8002/rest/phenotype/`+phenotypeId+`/similar.json`) // DEV CODE
    return fetch(`https://arapheno.1001genomes.org/rest/phenotype/${phenotypeId}/similar.json`)
        .then(checkStatus)
        .then(convertToModel);
}

export async function loadStudiesOfPhenotype(phenotypeId: number): Promise<Study[]> {
    return fetch(`/api/phenotypes/${phenotypeId}/studies/`)
        .then(checkStatus)
        .then<Study[]>(convertToModel);
}

export async function loadGenesByRegion(chr: string, start: number, end: number, features: boolean): Promise<Gene[]> {
    return fetch(`/api/genes/?chr=${chr}&start=${start}&end=${end}` + (features ? "&features" : ""))
        .then(checkStatus)
        .then<Gene[]>(convertToModel);
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
        .then<Gene>(convertToModel);
}
export async  function loadAssociationsOfGene(geneId, zoom: number, filter, page: number = 1, pageSize: number = 25) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = pageSize * (page - 1);
    let url = `/api/genes/${geneId}/associations/?limit=${pageSize}&offset=${offset}&zoom=${zoom}`;

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
export async function loadTopAssociations(filter, page, lastElement = [0, ""]): Promise<Association[]> {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = 25 * ( page - 1);
    let url = `/api/associations/`;
    if (lastElement[0] !== 0) {
        url += "?lastel=" + lastElement[0].toString() + "," + lastElement[1];
    } else {
        url += `?limit=25&offset=${offset}`;
    }
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then<Association[]>(convertToModel);
}
export async function loadTopKOMutations(filter, page, limit, lastElement = [0, ""]): Promise<KOAssociation[]> {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = limit * ( page - 1);
    let url = `/api/koassociations/`;
    if (lastElement[0] !== 0) {
        url += "?lastel=" + lastElement[0].toString() + "," + lastElement[1] + `&limit=${limit}`;
    } else {
        url += `?limit=${limit}&offset=${offset}`;
    }
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then<KOAssociation[]>(convertToModel);
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
export async function loadTopGenesList(filter, page: number = 1, pageSize: number = 25, KO: boolean = false) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    const offset = pageSize * (page - 1);
    let url: string;
    if (KO) {
        url = `/api/genes/top_ko_list/?limit=${pageSize}&offset=${offset}`;
    } else {
        url = `/api/genes/top_list/?limit=${pageSize}&offset=${offset}`;
    }
    if (queryParam) {
        url += queryParam;
    }
    return fetch(url)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadTopGenesAggregatedStatistics(filter) {
    const queryParam = getTopAssociationsParametersQuery(filter);
    let url = `/api/genes/top_list_aggregated_statistics/?`;
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
        .then<Gene[]>(convertToModel);
}

export async  function loadApiVersion(): Promise<ApiVersion> {
    return fetch("/api/version/")
        .then(checkStatus)
        .then<ApiVersion>(convertToModel);
}

export async function loadAssociation(id: string): Promise<Association> {
    return fetch(`/api/associations/${id}/`)
        .then(checkStatus)
        .then<Association>(convertToModel);
}

export async function loadAssociationDetails(id: string): Promise<Accession> {
    return fetch(`/api/associations/${id}/details`)
    .then(checkStatus)
    .then<Accession>(convertToModel);
}

export async function loadAssociationsHeatmap(): Promise<Array<{}>> {
    return fetch(`/api/associations/map_heat/`)
        .then(checkStatus)
        .then<Array<{}>>(convertToModel);
}
export async function loadAssociationsHeatmapZoomed(region=[0,0,0], regionwidth=25000): Promise<Array<{}>> {
    let url = `/api/associations/map_heat/`;
    if (region.length != 0){
        url += `?recompute=1&chromosome=${region[0]}&region=${region[1]}&region=${region[2]}&regionwidth=${regionwidth}`
    }
    return fetch(url)
        .then(checkStatus)
        .then<Array<{}>>(convertToModel);
}

export async function loadAssociationsHistogram(regionWidth: number): Promise<Array<{}>> {
    return fetch(`/api/associations/map_histogram/?region_width=${regionWidth}`)
        .then(checkStatus)
        .then<Array<{}>>(convertToModel);
}
export async function loadAssociationsHistogramZoomed(region=[0,0,0], regionWidth: number): Promise<Array<{}>> {
    return fetch(`/api/associations/map_histogram/?region_width=${regionWidth}&recompute=1&chromosome=${region[0]}&region=${region[1]}&region=${region[2]}`)
        .then(checkStatus)
        .then<Array<{}>>(convertToModel);
}
// export async function loadAssociation(): Promise<Association> {
//     return fetch(`/api/associations/map_heat/`)
//         .then(checkStatus)
//         .then<Array<{}>>(convertToModel);
// }
// TODO: implement rest functions for association retrieval.