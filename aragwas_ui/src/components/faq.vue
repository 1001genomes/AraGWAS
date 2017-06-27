<template>
    <div class="mt-0">
        <v-parallax src="/static/img/ara2.jpg" height="80">
            <div class="section">
                <div class="container mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                    <v-divider></v-divider>
                </div>
            </div>
        </v-parallax>
        <div class="container">
            <div class="section">
                <h4>General Information</h4>
                <v-expansion-panel expand class="mt-4 mb-4">
                    <v-expansion-panel-content v-for="faq in faqs_general" :key="faq">
                        <h6 class="mt-3 black--text" slot="header">{{ faq.question }}</h6>
                        <v-card class="grey lighten-4" >
                            <div class="pl-4 pt-3 pr-4 black--text" v-html="faq.html" v-if="faq.html">
                            </div>
                            <div class="pl-4 pt-3 pr-4 black--text" v-else> {{ faq.answer }}</div>
                            <br>
                        </v-card>
                    </v-expansion-panel-content>
                </v-expansion-panel>
                <h4>Tutorials</h4>
                <v-expansion-panel expand class="mt-4 mb-4">
                    <v-expansion-panel-content v-for="faq in faqs_tutorial" :key="faq">
                        <h6 class="mt-3 black--text" slot="header">{{ faq.question }}</h6>
                        <v-card class="grey lighten-4" >
                            <div class="pl-4 pt-3 pr-4 black--text" v-html="faq.html" v-if="faq.html">
                            </div>
                            <div class="pl-4 pt-3 pr-4 black--text" v-else> {{ faq.answer }}</div>
                            <br>
                        </v-card>
                    </v-expansion-panel-content>
                </v-expansion-panel>
                <h4>REST API</h4>
                <v-expansion-panel expand class="mt-4 mb-4">
                    <v-expansion-panel-content v-for="faq in faqs_rest" :key="faq">
                        <h6 class="mt-3 black--text" slot="header">{{ faq.question }}</h6>
                        <v-card class="grey lighten-4" >
                            <div class="pl-4 pt-3 pr-4 black--text" v-html="faq.html" v-if="faq.html">
                            </div>
                            <div class="pl-4 pt-3 pr-4 black--text" v-else> {{ faq.answer }}</div>
                            <br>
                        </v-card>
                    </v-expansion-panel-content>
                </v-expansion-panel>
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
    export default class FAQ extends Vue {
        breadcrumbs = [{text: "Home", href: "/"}, {text: "FAQ", href: "/faq", disabled: true}];
        faqs_general = [
            {question: "What is the AraGWASCatalog?", html:"The AraGWASCatalog is a central, standardised, quality controlled and manually curated repository for genome-wide association studies (GWAS) for the model organism <i>Arabidopsis thaliana</i>.\
                The repository provides several views to obtain an overview about top associated markers across all available phenotypes from the central and public <i>Arabidopsis thaliana</i> phenotype repository <a target=_blank href=https://arapheno.1001genomes.org>AraPheno</a>.<br/>\
                A full-text elasticsearch assists users to query the database for their favorite genes, traits or studies. Detailed views with interactive visualisations for genes, phenotypes and studies, help users to get an in-depth overview about the database's top associations.\
                Different filters can be used to further narrow down the search results, such as filtering SNPs for certain minor allele frequencies or genome annotations."},
            {question: "Is the data in the AraGWASCatalog public?", answer: "Yes, all data in the AraGWASCatalog is public. Please cite AraGWASCatalog, the phenotype and original study of the GWAS results when using data from the AraGWASCatalog."},
//            {question: "Is it possible to download the data from the AraGWASCatalog?", answer: "Yes, we provide (or will provide?!) different ways to download the data."}, // NOT available yet
            {question: "Which data is included?", html: "So far the AraGWASCatalog contains recomputed GWAS results using a standardised GWAS pipeline on all publicly available phenotypes from <a target=_blank href=https://arapheno.1001genomes.org>AraPheno</a>.\
                The catalog will be updated regularly when new phenotypes are published in <a target=_blank href=https://arapheno.1001genomes.org>AraPheno</a>. "}, // TODO: Arthur: add more info about the standard pipeline
            {question: "Why do we use a standardised GWAS pipeline and how does it look like?", answer: ""}, // TODO: complete
            {question: "Why do we provide two significance thresholds (Bonferroni and permutation based)?", answer: ""}, // TODO: complete
            {question: "How is the association score defined?", html: "The score of an associated hit is defined as: -log<sub>10</sub>(p-value)."},
            {question: "What does top associated mean?", answer: "The top associations of a study are all the associations that have a p-value below the fixed threshold of 1e-5 (i.e. score above 5). These values are stored in the fast elasticsearch database and displayed in the top associations lists."}, // TODO: add  "All associations are present in the HDF5 files." once download can be performed
        ];

        faqs_tutorial = [
            {question: "How does the global search work?", html: "The global search at the <router-link href=http://aragwas.1001genomes.org/>landing page</router-link> can be used to query the database for phenotype names, public GWAS studies, <i>A. thaliana</i> genes or SNP loci.\
                <br>\
                <strong>Search examples:</strong><br>\
                <ul>\
                    <li> Search for a phenotype: <code>FLC</code></li>\
                    <li> Search for a gene: <code>AT2G27035</code></li>\
                    <li> Search for a loci: <code>chr2:1153551</code></li>\
                </ul>"},
            {question: "How to find all top associated hits across all available studies?", html: "You can access a list of all top associated hits across all phenotypes and studies integrated into the AraGWASCatalog by clicking on the <a href=http://aragwas.1001genomes.org/#/top-associations>Top Associations</a> button in the <a href=http://aragwas.1001genomes.org/>landing page</a>.\
                The table contains all top associated hits sorted in descending order (SNP with strongest association at the top)."},
            {question: "How to get a list of genes that contain associated hits?", answer: "You can get a list of the top associated genes (i.e. genes with the highest number of significantly associated SNPs) on every study view as they are listed in the piechart."},
            {question: "How can I filter association tables?", answer: "Different filters are provided to filter the association tables. You can either filter the table by minor allele frequency (MAF), chromosome or different types of annotations (e.g. non-synonymous SNPs).\
                For some tables the filtering options have to be activated by clicking on the 'Controls' switch."},
            {question: "How to obtain detailed information about the Phenotype?", answer: "When clicking on the phenotype name you can get more detailed information about the phenotype and all hits that are associated with the phenotype.\
                A list of GWA studies is provided such that you get an overview in which GWAS experiments the phenotype was used. Another list present phenotypes with similar trait ontologies. Further, you can find a link to AraPheno, where you can download the phenotypic information."},
            {question: "How to obtain detailed information about the GWAS study?", answer: "When clicking on the study name you can get more detailed information about the GWAS study. The detailed study view contains detailed information about the number of significantly associated hits using a conservative Bonferroni correction as well as a permutation based significance threshold.\
                    Further, you can get an overview about the distribution of genes or different SNP types for all associated hits. The Manhattan Plot tab shows Manhattan plots for the selected study."}, // add interactive manhattan plots once hover functionality is done
            {question: "How to obtain a gene centric view?", answer: "If you click on a gene name, you will access the gene-centric view. There, all top associations lying in that genomic region are plotted and listed independently of their study so as to visualize areas associated to multiple phenotypes. If you have a favourite gene, this view will tell you which phenotypes are associated with it."},
        ];
        faqs_rest = [
            {question: "What is a REST API?", html: "REST is an abbreviation for representational state transfer. It can be used to retrieve data from AraPheno using certain URLs. You also can write custom scripts (e.g. in Python, Pearl, Java etc.) to request and download the information you need.<br>\
                More information can be found on Wikipedia: <a target=_blank href=https://en.wikipedia.org/wiki/Representational_state_transfer>What is REST?</a>"},
            {question: "How to access a detailed documentation about the REST API?", html: "Detailed information about all functions supported by the REST API from the AraGWASCatalog can be accessed here: <a target=_blank href=http://aragwas.1001genomes.org/docs/>AraGWASCatalog REST API Documentation</a>"},
        ]


    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    h6 {
        font-weight: 400;
    }
    .section {
        padding-top: 1rem;
    }

</style>
