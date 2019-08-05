import Gene from "./gene";
import Study from "./study";

interface KOAssociation {
    score: number;
    beta: number;
    seBeta: number;
    study: Study;
    gene: Gene;
    maf: number;
    mac: number;
    annotation: string;
    type: boolean;
    selected: boolean;
    significant: boolean;

}
export default KOAssociation;
