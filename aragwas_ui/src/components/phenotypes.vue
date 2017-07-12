<template>
    <div class="mt-0">
        <v-parallax src="/static/img/ara2.jpg" height="80">
        <div class="section">
            <div class="mb-2">
                <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
            </div>
        </div>
        </v-parallax>
        <div class="page-container">
            <div class="section">
                <v-data-table
                        v-bind:headers="columns"
                        v-bind:items="phenotypes"
                        v-bind:pagination.sync="pagination"
                        hide-actions
                        :loading="loading"
                        :total-items="totalItems"
                        class="elevation-1"
                >
                    <template slot="headers" scope="props" class="text-xs-left">
                        {{ props.item.text }}
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
        columns = [{text: "Name", left:true, value: "name"},{text: "Description", left: true, value: "description"},{text: "# Studies", value: "n_studies"}];
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, descending: false, sortBy: "name"};
        search: string = '';
        filterKey: string = "";
        phenotypes = [];
        currentPage = 1;
        pageCount = 5;
        totalItems: number = 0;
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Phenotypes", href: "phenotypes", disabled: true}];

        @Watch("pagination")
        onPaginationChanged(val: {}, oldVal: {}) {
            // only load when sorting is changed
            if (val["sortBy"] != oldVal["sortBy"] || val["descending"] != oldVal["descending"]) {
                this.loading = true;
                this.loadData(val, this.currentPage);
            }
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
            this.totalItems = data.count;
            this.pageCount = data.pageCount;
            this.loading = false;
        }

    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .section {
        width: 90%;
        padding-top: 1rem;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>
