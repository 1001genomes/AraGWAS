interface Page<T> {
    items: T[];
    pageCount: number;
    current_page: number;
    count: number;
}

export default Page;
