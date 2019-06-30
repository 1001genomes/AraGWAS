interface Accession {
    accessionId: number;
    accessionName: string;
    phenotypeValue: number;
    accessionLongitude: number;
    accessionLatitude: number;
    accessionCountry: string;
    allele: string;
    obsUnitId: number;
}

export default Accession;
