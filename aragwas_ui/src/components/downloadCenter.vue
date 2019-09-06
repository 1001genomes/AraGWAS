<template>
    <div class="mt-0">
        <v-parallax src="/static/img/ara2.jpg" height="80">
            <div class="section">
                <div class="container mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                    <!-- <v-divider></v-divider> -->
                </div>
            </div>
        </v-parallax>
        <div class="container">
            <div class="section">
                <h4>AraGWAS Database download</h4>
                <div class='mb-5'>
                    <v-card>
                        <v-card-text>
                            <p >Download all GWAS associations scores recorded in AraGWAS here in the HDF5 format. This may take a while.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1 mb-3" light  tag="a" :href="'/api/studies/bulk_download'" download v-tooltip:right="{html: 'Download AraGWAS in bulk'}">
                                <v-icon left dark>file_download</v-icon> Full GWAS DB Download
                            </v-btn>
                            <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">public</v-icon> Citation</div>
                            <div>
                                <p>
                                    Please cite the following publication when using this dataset.
                                </p>
                                <p class="light">
                                    Matteo Togninalli, Ümit Seren, Dazhe Meng, Joffrey Fitz, Magnus Nordborg, Detlef Weigel, Karsten Borgwardt, Arthur Korte, and Dominik G. Grimm; <b>The AraGWAS Catalog: a curated and standardized Arabidopsis thaliana GWAS catalog;</b> Nucleic Acids Research, gkx954, <a target=_blank href=https://doi.org/10.1093/nar/gkx954>https://doi.org/10.1093/nar/gkx954</a>
                                </p>
                            </div>
                        </v-card-text>
                    </v-card>
                </div>
                <h4>KO Mutation download</h4>
                <div class='mb-5'>
                    <v-card>
                        <v-card-text>
                                <p >Download all KO mutation associations scores in AraGWAS here in the csv format.</p>
                                <v-btn dark class="btn--large icon--left green lighten-1 mb-3" light  tag="a" :href="'/api/koassociations/bulk_download'" download v-tooltip:right="{html: 'Download KO Mutations association scores in bulk'}">
                                    <v-icon left dark>file_download</v-icon> KO Associations Download
                                </v-btn>
                                <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">public</v-icon> Citation</div>
                                <div>
                                    <p>
                                        Please cite the following publication when using this dataset.
                                    </p>
                                    <p class="light">
                                        Matteo Togninalli, Ümit Seren, Dazhe Meng, Joffrey Fitz, Magnus Nordborg, Detlef Weigel, Karsten Borgwardt, Arthur Korte, and Dominik G. Grimm (2018) <b>The AraGWAS Catalog: a curated and standardized Arabidopsis thaliana GWAS catalog;</b> Nucleic Acids Research, gkx954, <a target=_blank href=https://doi.org/10.1093/nar/gkx954>https://doi.org/10.1093/nar/gkx954</a>
                                    </p>
                                </div>
                        </v-card-text>
                    </v-card>
                        <v-card>
                            <v-card-text>
                                <p >Additionally, you can download the original KO mutation file here.</p>
                                <v-btn dark class="btn--large icon--left green lighten-1 mb-3" light  tag="a" :href="'/api/koassociations/original_mutations'" download v-tooltip:right="{html: 'Download KO mutations'}">
                                    <v-icon left dark>file_download</v-icon> KO Mutations Download
                                </v-btn>
                                <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">public</v-icon> Citation</div>
                                <div>
                                    <p>
                                        Please cite the following publication when using this dataset.
                                    </p>
                                    <p class="light">
                                        Monroe, J. Grey, Tyler Powell, Nicholas Price, Jack L. Mullen, Anne Howard, Kyle Evans, John T. Lovell, and John K. McKay (2018) <b>Drought adaptation in Arabidopsis thaliana by extensive genetic loss-of-function.</b> Elife, 7, e41038.<a target=_blank href=https://doi.org/10.7554/eLife.41038.001>https://doi.org/10.7554/eLife.41038.001</a>
                                    </p>
                                </div>
                    </v-card-text>
                </v-card>
                </div>
                <h4>Genotype download</h4>
                <v-card>
                        <v-card-text>
                                <p >Download the imputed genotype used for all current associations in AraGWAS here.</p>
                                <v-btn dark class="btn--large icon--left green lighten-1 mb-3" light  tag="a" :href="'/api/genotypes/download'" download v-tooltip:right="{html: 'Download the genotype matrix'}">
                                    <v-icon left dark>file_download</v-icon> Genotype Download
                                </v-btn>
                                <p class="mt-3">For other genotype versions, please refer to this <a href="https://drive.google.com/open?id=0BwYlrRGOfVARS01aMnFVVWotbXc">google drive page</a>.</p>
                            <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">public</v-icon> Citation</div>
                                <div>   
                                    <p>
                                        Please cite the following publications when using this dataset.
                                    </p>
                                    <p class="light">
                                        Matteo Togninalli, Ümit Seren, Dazhe Meng, Joffrey Fitz, Magnus Nordborg, Detlef Weigel, Karsten Borgwardt, Arthur Korte, and Dominik G. Grimm (2018) <b>The AraGWAS Catalog: a curated and standardized Arabidopsis thaliana GWAS catalog;</b> Nucleic Acids Research, gkx954, <a target=_blank href=https://doi.org/10.1093/nar/gkx954>https://doi.org/10.1093/nar/gkx954</a>
                                    </p>
                                    <p class="light">
                                        The 1001 Genomes Consortium (2016) <b>1,135 genomes reveal the global pattern of polymorphism in Arabidopsis thaliana.</b> Cell 166, no. 2: 481-491.<a target=_blank href=https://doi.org/10.1016/j.cell.2016.05.063>https://doi.org/10.1016/j.cell.2016.05.063</a>
                                    </p>
                                </div>
                        </v-card-text>
                    </v-card>
                
            </div>
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch} from "vue-property-decorator";
    import Breadcrumbs from './breadcrumbs.vue'

    @Component({
        components: {
            "breadcrumbs": Breadcrumbs,
        },
    })
    export default class DownloadCenter extends Vue {
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Download Center", href: "faq", disabled: true}];

    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
    @import "../stylus/main"

    h4
        color:$theme.primary

    h6 {
        font-weight: 400;
    }
    .section {
        padding-top: 1rem;
    }

</style>
