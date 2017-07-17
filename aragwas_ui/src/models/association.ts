import Study from "./study";

interface Association {
    chr: string;
    position: number;
    score: number;
    study: Study;
    gene: string;
    maf: number;
    annotation: string;
    type: boolean;
    snp: SNP;
    selected: boolean;

    highlighted: boolean;
}
interface SNP {
    chr: string;
    position: string;
}
export default Association;
