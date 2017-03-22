import Page from '@/models/page';
import Study from '@/models/study';

// TODO convert to Typescript
function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response;
  } else {
    var error = new Error(response.statusText)
    throw error;
  }
}

// TODO convert to Typescript
function convertToModel(response) {
    return response.json();
}

export async function loadStudies () {
    return fetch('http://localhost:3000/api/studies')
        .then(checkStatus)
        .then(convertToModel);
}