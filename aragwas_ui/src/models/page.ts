interface Page<T> {
    items: T[];
    pageCount: number;
    pageSize: number;
    pageIndex: number;
    totalCount: number;
}

export default Page;