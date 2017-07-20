interface Study {
    id: number;
    name: string;
    transformation: string;
    method: string;
    phenotype: string;
}

export default Study;

export class ManhattanPlotOptions {
    constructor(readonly chr: number, readonly max_x: number,
                readonly max_y: number, readonly bonferroniThreshold: number, readonly color: number
    ) {
    }
}