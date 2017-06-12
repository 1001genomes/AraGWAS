type GeneAlias = [string, string];
type Allele = string;

interface SNPMap {
    [pos: number]: SNP;
}

export class GenePlotOptions {
    constructor(readonly chr: string,
                readonly startPos: number, readonly endPos: number,
                readonly maxScore: number, readonly bonferoniThreshold: number,
                ) {
    }
}

interface Annotation {
    readonly effect: string;
    readonly impact: string;
    readonly function: string;
    readonly codonChange: string;
    readonly aminoAcidChange: string;
    readonly rank: number;
    readonly transcriptId: number;
}

interface SNP {
    readonly position: number;
    readonly ref: Allele;
    readonly alt: Allele;
    readonly anc: Allele;
    readonly chr: string;
    readonly coding: boolean;
    readonly annotations?: Annotation[];
}

interface GenePosition {
    readonly gte: number;
    readonly lte: number;
}

interface CDS {
    readonly postions: GenePosition;
    readonly frame: number;
}

interface Exon {
    readonly positions: GenePosition;
}

interface UTR {
    readonly positions: GenePosition;
}

interface Isoform {
    readonly name: string;
    readonly strand: string;
    readonly type: string;
    readonly description: string;
    readonly cds: CDS[];
    readonly exons: Exon[];
    readonly utr5: UTR;
    readonly utr3: UTR;
}

interface Gene {
    readonly id: string;
    readonly name: string;
    readonly chr: string;
    readonly type: string;
    readonly positions: GenePosition;
    readonly strand: string;
    readonly aliases?: GeneAlias[];
    readonly isoforms?: Isoform[];
    readonly snps?: SNPMap;
}
export default Gene;