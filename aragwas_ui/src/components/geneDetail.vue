<template>
    <div>
        <div class="banner-container" style="height: 70px">
            <div class="section" id="head">
                <div class="container mt-3">
                    <v-breadcrumbs icons divider="chevron_right" class="left">
                        <v-breadcrumbs-item
                                v-for="item in breadcrumbs" :key="item"
                                :disabled="item.disabled"
                                class="breadcrumbsitem"
                                :href=" item.href "
                                target="_self"
                        >
                            <h5 v-if="item.disabled">{{ item.text }}</h5>
                            <h5 v-else class="green--text">{{ item.text }}</h5>
                        </v-breadcrumbs-item>
                    </v-breadcrumbs>
                    <v-divider></v-divider>
                </div>
            </div>
        </div>
        <v-container>
            <v-row>
                <v-col xs4>
                    <v-text-field name="geneName-search" :value="geneName" prepend-icon="search"></v-text-field>
                </v-col>
                <!--<v-col xs4 offset-xs4>-->
                    <!--<v-slider v-model="zoom" prepend-icon="zoom_in"></v-slider>-->
                <!--</v-col>-->
            </v-row>
            <v-row>
                <br>
                <v-col xs12>
                    <div id="genomic-region">
                        <v-row><v-col xs5><h5 class="mb-1">Genomic Region</h5><v-divider></v-divider></v-col>
                            <v-col xs4 offset-xs3><v-slider v-model="zoom" prepend-icon="zoom_in" permanent-hint hint="Zoom"></v-slider></v-col></v-row>
                        <!--INSERT DRAWING HERE-->
                        <br>
                        <br>
                        <br>
                        <h2 style="justify-content: center; display: flex">INSERT DRAWING HERE</h2>
                        <br>
                        <br>
                        <br>
                    </div>
                </v-col>
            </v-row>
            <v-row>
                <br>
                <v-col xs12>
                    <div id="associations-list">
                        <v-row><v-col xs5><h5 class="mb-1">Associations List</h5><v-divider></v-divider></v-col></v-row>
                        <v-card class="mt-3">
                            <table class="table">
                                <thead>
                                <tr>
                                    <th v-for="key in columns">
                                        {{ key | capitalize }}
                                    </th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr v-for="entry in filteredData">
                                    <td v-for="key in columns">
                                        <div>{{entry[key]}}</div>
                                    </td>
                                </tr>
                                </tbody>
                            </table>
                        </v-card>
                        <div class="page-container mt-5 mb-3">
                            <v-pagination :length.number="pageCount" v-model="currentPage" />
                        </div>
                    </div>
                </v-col>
            </v-row>
        </v-container>
    </div>
</template>

<script lang="ts">
    import Vue from 'vue';
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import {loadAssociationsOfGene, loadGene} from '../api';

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
    })
    export default class GeneDetail extends Vue {
        // Gene information
        @Prop()
        geneId: string = '';
        geneName: string = '';
        geneDescription: string = '';
        startPosition = 0;
        endPosition = 0;
        chromosome = 0;
        snpSet;
        snpCount = 0;
        associationCount = 0;

        // Associations parameters
        ordered: string;


        breadcrumbs = [{text: 'Home', href: '/'}, {text:'Genes', href: '#/genes'}, {text: this.geneName, href: '', disabled: true}];
        zoom = 1;
        pageCount = 5;
        currentPage = 1;
        totalCount = 0;
        columns = ['SNP', 'p-value', 'phenotype', 'gene','maf','beta', 'odds ratio', 'confidence interval'];
        filterKey: string = '';
        associations = [];

        get filteredData() {
            let filterKey = this.filterKey;
            if (filterKey) {
                filterKey = filterKey.toLowerCase();
            }
            let data = this.associations;
            if (filterKey) {
                data = data.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
                    });
                });
            }
            return data;
        }

        created(): void {
            if (this.$route.params.geneId) {
                this.geneId = this.$route.params.geneId;
            }
            loadGene(this.geneId).then(this._displayGeneData);
            this.loadData(this.currentPage);
        }

        // Gene DATA LOADING
        _displayGeneData(data): void {
            this.geneName = data.name;
            this.geneDescription = data.description;
            this.breadcrumbs[2].text = data.name;
            this.startPosition = data.start_position;
            this.endPosition = data.end_position;
            this.chromosome = data.chromosome;
            this.snpSet = data.SNPs;
            this.snpCount = data.SNP_count;
            this.associationCount = data.associationCount;
        }
        // ASSOCIATION LOADING
        loadData(page: number): void {
            // Load associations of all cited SNPs
            loadAssociationsOfGene(this.geneId, page, this.ordered).then(this._displayData)
        }
        _displayData(data): void {
            this.associations = data.results;
            this.currentPage = data.current_page;
            this.totalCount = data.count;
            this.pageCount = data.page_count;
        }

    }
</script>

<style scoped>
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>