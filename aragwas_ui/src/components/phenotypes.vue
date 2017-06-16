<template>
    <div class="mt-0">
        <v-parallax src="/static/img/ara2.jpg" height="80">
        <div class="section">
            <div class="container mt-2">
                <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
            </div>
        </div>
        </v-parallax>
        <div class="container">
            <div class="section">
                <v-data-table
                        v-bind:headers="columns"
                        v-bind:items="phenotypes"
                        v-bind:pagination.sync="pagination"
                        hide-actions
                        :loading="loading"
                        class="elevation-1"
                >
                    <template slot="headers" scope="props" class="text-xs-left">
                        <span class="text-xs-left">
                          {{ props.item.text | capitalize }}
                        </span>
                    </template>
                    <template slot="items" scope="props">
                        <td><router-link :to="{name: 'phenotypeDetail', params: { id: props.item.pk }}">{{ props.item.name }}</router-link></td>
                        <td>{{ props.item.description }}</td>
                        <td  class="text-xs-right">{{ props.item.studySet.length }}</td>
                    </template>
                </v-data-table>
            </div>
        </div>
        <div class="page-container mt-2 mb-3">
            <v-pagination :length.number="pageCount" v-model="currentPage" />
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch} from "vue-property-decorator";

    import {loadPhenotypes} from "../api";
    import Page from "../models/page";
    import Study from "../models/study";
    import Breadcrumbs from './breadcrumbs.vue'

    @Component({
        filters: {
            capitalize(str) {
                str = str.split("_").join(" ");
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
        components: {
            "breadcrumbs": Breadcrumbs,
        },
    })
    export default class Phenotypes extends Vue {
        loading: boolean = false;
        studyPage: Page<Study>;
        sortOrders = {name: 1, description: 1, n_studies: 1};
        sortKey: string = "";
        ordered: string = "";
        columns = [{text: "name", value: "name"},{text: "description", value: "description"},{text: "n_studies", value: "n_studies"}];
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name};
        search: string = '';
        filterKey: string = "";
        phenotypes = [];
        currentPage = 1;
        pageCount = 5;
        totalCount = 0;
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Phenotypes", href: "phenotypes", disabled: true}];

        @Watch("pagination")
        onPaginationChanged(val: {}, oldVal: {}) {
            this.loading = true;
            this.loadData(val, this.currentPage);
        }
        @Watch("currentPage")
        onPaginationPageChanged(val: number, oldVal: number) {
            this.loading = true;
            this.loadData(this.pagination, val);
        }
        created(): void {
            this.loading = true;
            this.loadData(this.pagination, this.currentPage);
        }
        loadData(pagination, page: number): void {
            const {sortBy, descending} = pagination;

            let ordered = '';
            if (sortBy === null){
                ordered = '';
            } else {
                if (descending) {
                    ordered = "-"+sortBy;
                } else {
                    ordered = sortBy;
                }
            }
            loadPhenotypes(page, ordered).then(this._displayData);
        }
        _displayData(data): void {
            this.phenotypes = data.results;
            this.currentPage = data.currentPage;
            this.pagination.totalItems = data.count;
            this.pageCount = data.pageCount;
            this.loading = false;
        }

    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    .banner-container {
        position: relative;
        overflow: hidden;
    }
    .section {
        padding-top: 1rem;
    }
    .table {
        width: 100%;
        max-width: 100%;
        margin-bottom: 2rem;
    }
    .parallax-container  {
        position:absolute;
        top:0;
        left:0;
        right:0;
        bottom:0;
        z-index:-1;
    }
    .arrow {
        display: inline-block;
        vertical-align: middle;
        width: 0;
        height: 0;
        margin-left: 5px;
        opacity: 0;
    }

    .arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid green;
    }

    .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid green;
    }
    .table th {
        text-align:left;
    }

    th.active {
        color:black;
    }

    th.active .arrow {
        opacity: 1;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>
