<template>
    <div class="mt-0">
        <div class="banner-container" style="height: 80px">
            <div class="section">
                <div class="container mt-2">
                    <v-breadcrumbs icons divider="chevron_right" class="left white--text" style="font-size: 24pt">
                        <v-breadcrumbs-item
                                v-for="item in breadcrumbs" :key="item"
                                :disabled="item.disabled"
                                class="breadcrumbsitem"
                                :href=" item.href "
                                target="_self"
                        >
                            <h4 v-if="item.disabled" class="grey--text text--lighten-2">{{ item.text }}</h4>
                            <h4 v-else class="white--text">{{ item.text }}</h4>
                        </v-breadcrumbs-item>
                    </v-breadcrumbs>
                    <v-divider></v-divider>
                </div>
            </div>
            <v-parallax class="parallax-container" src="/static/img/ara5.jpg" height="80">
            </v-parallax>
        </div>
        <div class="container">
            <div class="section">
                <v-row>
                    <v-col xs12><h5 class="mb-2 mt-3"><v-icon class="green--text lighten-1" style="vertical-align: middle;">trending_up</v-icon> Top Associations</h5><v-divider></v-divider></v-col>
                </v-row>
                <v-row>
                    <v-col xs3>
                        <h6 class="mt-4">MAF</h6>
                            <v-switch v-model="maf" primary label="<1% ( % of SNPs)" value="<1" class="mb-0"></v-switch>
                            <v-checkbox v-model="maf" primary label="1-5% ( % of SNPs)" value="1-5" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="maf" primary label="5-10% ( % of SNPs)" value="5-10" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="maf" primary label=">10% ( % of SNPs)" value=">10" class="mt-0"></v-checkbox>
                        <h6 class="mt-4">Chromosomes</h6>
                            <v-checkbox v-model="chr" warning label="1 ( % of SNPs)" value="1" class="mb-0"></v-checkbox>
                            <v-checkbox v-model="chr" primary label="2 ( % of SNPs)" value="2" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="chr" info label="3 ( % of SNPs)" value="3" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="chr" error label="4 ( % of SNPs)" value="4" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="chr" label="5 ( % of SNPs)" value="5" class="mt-0"></v-checkbox>
                        <h6 class="mt-4">Annotation</h6>
                            <v-checkbox v-model="annotation" primary label="NS ( % of SNPs)" value="NS" class="mb-0"></v-checkbox>
                            <v-checkbox v-model="annotation" primary label="S ( % of SNPs)" value="S" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="annotation" primary label="* ( % of SNPs)" value="*" class="mt-0 mb-0"></v-checkbox>
                        <h6 class="mt-4">Type</h6>
                            <v-checkbox v-model="type" primary label="Genic ( % of SNPs)" value="genic" class="mb-0"></v-checkbox>
                            <v-checkbox v-model="type" primary label="Non-genic ( % of SNPs)" value="non-genic" class="mt-0 mb-0"></v-checkbox>
                    </v-col>
                    <v-col xs9>
                        <table class="table">
                            <thead>
                            <tr>
                                <th v-for="key in columns"
                                    @click="sortBy(key)"
                                    :class="{ active: sortKey == key }"
                                    style="font-size: 11pt">
                                    {{ key | capitalize }}
                                    <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'"></span>
                                </th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="entry in filteredData">
                                <td v-for="key in columns">
                                    <router-link v-if="(key==='name')" :to="{name: 'studyDetail', params: { studyId: entry['pk'] }}" >{{entry[key]}}</router-link>
                                    <router-link v-else-if="(key==='phenotype')" :to="{name: 'phenotypeDetail', params: { phenotypeId: entry['phenotype_pk'] }}" >{{entry[key]}}</router-link>
                                    <div v-else>{{entry[key]}}</div>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                        <div class="page-container mt-5 mb-3">
                            <v-pagination :length.number="pageCount" v-model="currentPage" />
                        </div>
                    </v-col>
                </v-row>
            </div>
        </div>
    </div>
</template>


<script lang="ts">
    import {Component, Watch} from 'vue-property-decorator';
    import {loadStudies} from '../api';
    import Page from '../models/page';
    import Study from '../models/study';
    import Vue from 'vue';

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
    })
    export default class TopAssociations extends Vue {
        loading: boolean = false;
        studyPage: Page<Study>;
        sortOrders = {name: 1, phenotype: 1, transformation: 1, method: 1, genotype: 1};
        sortKey: string = '';
        ordered: string = '';
        columns = ['SNP', 'p-value', 'phenotype', 'gene','maf','beta', 'odds ratio', 'confidence interval'];
        filterKey: string = '';
        studies = [];
        currentPage = 1;
        pageCount = 5;
        totalCount = 0;
        breadcrumbs = [{text: 'Home', href: '/'}, {text:'Top Associations', href: '#/top-associations', disabled: true},];
        maf = ['<1', '1-5', '5-10', '>10'];
        chr = ['1','2','3','4','5'];
        annotation = ['NS', 'S', '*'];
        type = ['genic','non-genic'];

        get filteredData() {
            let filterKey = this.filterKey;
            if (filterKey) {
                filterKey = filterKey.toLowerCase();
            }
            let data = this.studies;
            if (filterKey) {
                data = data.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
                    });
                });
            }
            return data;
        }

        @Watch('currentPage')
        onCurrentPageChanged(val: number, oldVal: number) {
            this.loadData(val);
        }
        @Watch('maf')
        onMafChanged(val: number, oldVal: number) {
            this.loadData(val);
        }
        @Watch('chr')
        onChrChanged(val: number, oldVal: number) {
            this.loadData(val);
        }
        @Watch('annotation')
        onAnnotationChanged(val: number, oldVal: number) {
            this.loadData(val);
        }
        @Watch('type')
        onTypeChanged(val: number, oldVal: number) {
            this.loadData(val);
        }
        created(): void {
            this.loadData(this.currentPage);
        }
        loadData(page: number): void {
            loadStudies(page, this.ordered).then(this._displayData);
        }
        _displayData(data): void {
            this.studies = data.results;
            this.currentPage = data.current_page;
            this.totalCount = data.count;
            this.pageCount = data.page_count;
        }
        sortBy(key): void {
            this.sortKey = key;
            this.sortOrders[key] = this.sortOrders[key] * -1;
            if (this.sortOrders[key] < 0) {
                this.ordered = '-' + key;
            } else {
                this.ordered = key;
            }
            this.loadData(this.currentPage);
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
