import Annotation from "./annotation";
import Study from "./study";

interface Association {
    score: number;
    study: Study;
    gene: string;
    maf: number;
    overPermutation: boolean;
    overFDR: boolean;
    type: boolean;
    snp: SNP;
    selected: boolean;

    highlighted: boolean;
}
interface SNP {
    chr: string;
    position: number;
    annotations: Annotation[];
    alt: string;
    anc: string;
    ref: string;
    coding: boolean;
    geneName: string;
}
export default Association;