interface Association {
    chr: string;
    position: number;
    score: number;
    study: string;
    gene: string;
    maf: number;
    annotation: string;
    type: boolean;
    snp: SNP;
    selected: boolean;
}
interface SNP {
    chr: string;
    position: string;
}
export default Association;