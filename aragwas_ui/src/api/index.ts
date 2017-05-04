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

export async function loadStudies(page= 1, ordered= '') {
    return fetch(`/api/studies/?page=${page}&ordering=${ordered}`)
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
// Import single study results, loads all associations refered to that study ID
export async  function loadStudy(studyID= '1') {
    return fetch(`/api/studies/${studyID}`)
        .then(checkStatus)
        .then(convertToModel);
}
export async  function loadAssociationsOfStudy(studyID= '1', page= 1, ordering= '-pvalue') {
    return fetch(`/api/associations_of_study/${studyID}/?page=${page}&ordering=${ordering}`)
        .then(checkStatus)
        .then(convertToModel);
}
