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
                    <p >Download all GWAS associations scores recorded in AraGWAS here in the HDF5 format. This may take a while.</p>
                    <v-btn dark class="btn--large icon--left green lighten-1" light  tag="a" :href="'/api/studies/bulk_download'" download v-tooltip:right="{html: 'Download AraGWAS in bulk'}">
                        <v-icon left dark>file_download</v-icon> Full GWAS DB Download
                    </v-btn>
                </div>
                <h4>KO Mutation download</h4>
                <div class='mb-3'>
                    <p >Download all KO mutation associations scores in AraGWAS here in the csv format.</p>
                    <v-btn dark class="btn--large icon--left green lighten-1" light  tag="a" :href="'/api/koassociations/bulk_download'" download v-tooltip:right="{html: 'Download KO Mutations association scores in bulk'}">
                        <v-icon left dark>file_download</v-icon> KO Associations Download
                    </v-btn>
                </div>
                <div class='mb-5'>
                    <p >Additionally, you can download the original KO mutation file here.</p>
                    <v-btn dark class="btn--large icon--left green lighten-1" light  tag="a" :href="'/api/koassociations/original_mutations'" download v-tooltip:right="{html: 'Download KO mutations'}">
                        <v-icon left dark>file_download</v-icon> KO Mutations Download
                    </v-btn>
                </div>
                <h4>Genotype downloads</h4>
                <div class='mb-5'>
                    <p >Download the imputed genotype used for all current associations in AraGWAS here.</p>
                    <v-btn dark class="btn--large icon--left green lighten-1" light  tag="a" :href="'/api/genotypes/download'" download v-tooltip:right="{html: 'Download the genotype matrix'}">
                        <v-icon left dark>file_download</v-icon> Genotype Download
                    </v-btn>
                    <p class="mt-3">For other genotype versions, please refer to this <a href="">google drive page</a>.</p>
                </div>
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
        
        faqs_tutorial = [
            {question: "How does the global search work?", html: "The global search at the <router-link href=http://aragwas.1001genomes.org/>landing page</router-link> can be used to query the database for phenotype names, public GWAS studies, <i>A. thaliana</i> genes or SNP loci.\
                <br>\
                <strong>Search examples:</strong><br>\
                <ul>\
                    <li> Search for a phenotype: <code>FLC</code></li>\
                    <li> Search for a gene: <code>AT2G27035</code></li>\
                    <li> Search for a loci: <code>chr2:1153551</code></li>\
                </ul>"},
            {question: "How to find all top associated hits across all available studies?", html: "You can access a list of all top associated hits across all phenotypes and studies integrated into the AraGWAS Catalog by clicking on the <a href=http://aragwas.1001genomes.org/#/top-associations>Top Associations</a> button in the <a href=http://aragwas.1001genomes.org/>landing page</a>.\
                The table contains all top associated hits sorted in descending order (SNP with strongest association at the top)."},
            {question: "How to get a list of genes that contain associated hits?", answer: "You can get a list of the top associated genes (i.e. genes with the highest number of significantly associated SNPs) on every study view as they are listed in the piechart."},
            {question: "How can I filter association tables?", answer: "Different filters are provided to filter the association tables. You can either filter the table by minor allele frequency (MAF), chromosome or different types of annotations (e.g. non-synonymous SNPs).\
                For some tables the filtering options have to be activated by clicking on the 'Controls' switch."},
            {question: "How to obtain detailed information about the Phenotype?", answer: "When clicking on the phenotype name you can get more detailed information about the phenotype and all hits that are associated with the phenotype.\
                A list of GWA studies is provided such that you get an overview in which GWAS experiments the phenotype was used. Another list present phenotypes with similar trait ontologies. Further, you can find a link to AraPheno, where you can download the phenotypic information."},
            {question: "How to obtain detailed information about the GWAS study?", answer: "When clicking on the study name you can get more detailed information about the GWAS study. The detailed study view contains detailed information about the number of significantly associated hits using a conservative Bonferroni correction as well as a permutation based significance threshold.\
                    Further, you can get an overview about the distribution of genes or different SNP types for all associated hits. The Manhattan Plot tab shows Manhattan plots for the selected study."}, // add interactive manhattan plots once hover functionality is done
            {question: "How to obtain a gene centric view?", answer: "If you click on a gene name, you will access the gene-centric view. There, all top associations lying in that genomic region are plotted and listed independently of their study so as to visualize areas associated to multiple phenotypes. If you have a favourite gene, this view will tell you which phenotypes are associated with it."},
            {question: "How to download my results?", html: "After filtering, you can get the associations you are interested in by clicking on the download button at the bottom of the filtering panel. This will generate a custom csv file with information about the associations you are interested in. You can also obtain the entire dataset of a specific study in the HDF5 format by clicking on the download button at the top right corner of the study view. Additionally, you can download the bulk data with all associations in AraGWAS from the <a href=http://aragwas.1001genomes.org/#/>homepage</a>."},
            {question: "What information is present in the csv file?", answer: "The downloadable csv files contains general information about the association (score, MAF, MAC and boolean values to state whether the score is above a certain threshold), the study (name, id, phenotype, genotype and thresholds) the SNP of interest (chromosome, position, reference and alternate alleles and potential annotations of the SNP)."},
            {question: "How can I get an overview of the genes with the largest number of associations?", html: "You can see a list of genes with the highest number of associations under the <a href=http://aragwas.1001genomes.org/#/top-genes/>Top Genes</a> view."},
            {question: "What is the GWAS Hitmap?", html: "The <a href=http://aragwas.1001genomes.org/#/map/>GWAS Hitmap</a> gives a quick overview of the highest-scoring SNPs across the <i>Arabidopsis thaliana</i> genome for all studies in the AraGWAS Catalog."},
        ];
        faqs_rest = [
            {question: "What is a REST API?", html: "REST is an abbreviation for representational state transfer. It can be used to retrieve data from the AraGWAS Catalog using certain URLs. You also can write custom scripts (e.g. in Python, Pearl, Java etc.) to request and download the information you need.<br>\
                More information can be found on Wikipedia: <a target=_blank href=https://en.wikipedia.org/wiki/Representational_state_transfer>What is REST?</a>"},
            {question: "How to access a detailed documentation about the REST API?", html: "Detailed information about all functions supported by the REST API from the AraGWAS Catalog can be accessed here: <a target=_blank href=http://aragwas.1001genomes.org/docs/>AraGWAS Catalog REST API Documentation</a>"},
            {question: "How to query the REST API?", html: "The REST API endpoints are language-independent and can be accessed via URL extensions. You can request any REST URL in your favourite environment. Here are some examples of how to get all available studies in JSON format\
                    <ul>\
                        <li> <b>Direct browser access</b> You can access the list directly in your browser through the following url: <a target=_blank href=https://aragwas.1001genomes.org/api/studies/>https://aragwas.1001genomes.org/api/studies/</a></li>\
                        <li> <b>Command-line request</b> Alternatively, you can request the information from your command-line tool: <code>$:> curl https://aragwas.1001genomes.org/api/studies/</code></li>\
                        <li> <b>In python</b> Finally, you can get the JSON-formatted data in python (or in other programming languages):<br />\
                            <code>import requests, sys</code><br />\
                            <code>r = requests.get(“https://aragwas.1001genomes.org/api/studies/”,headers={“Content-Type”:”application/json”})</code><br />\
                            <code>#Get Results</code><br />\
                            <code>results = r.json()</code><br />\
                            <code>print(results)</code></li>\
                    </ul>"},
            {question: "What are the filters I can use in several REST endpoints?", html: "There are several filter options one can use, these filters require you to list all your requests one by one, if left blank, no filter for that criteria is applied:\
                <ul>\
                    <li> Chromosomes: <code>chr</code>, the categories are [1, 2, 3, 4, 5]. Example: <code>chr=1&chr=4&chr=3</code></li>\
                    <li> Minor Allele Frequency: <code>maf</code>, the categories are [1, 1-5, 5-10, 10] for <1%, 1-5%, 5-10% and >10%. Example: <code>maf=1&maf=1-5</code></li>\
                    <li> Minor Allele Count: <code>mac</code>, the categories are [0,5] including 0 will also include associations for which MAC≤5. Example: <code>mac=5</code></li>\
                    <li> Annotation: <code>annotation</code>, the categories are [ns, s, in, i] for [Non-Synonymous coding, Synonymous coding, Intron, Intergenic] respectively. Example: <code>annotation=in&annotation=i</code></li>\
                    <li> Type: <code>type</code>, the categories are [genic, non-genic]. Example: <code>type=genic</code></li>\
                    <li> Significant: <code>significant</code>, only keeps significant associations, the categories are [0, b, p] for [no threshold, bonferroni-significant, permutation-significant]. Example: <code>significant=p</code></li>\
                </ul>\
                One can also filter by genomic region, study or phenotype using the gene, study and phenotype-based views. \
                A final request might look like: <code>https://aragwas.1001genomes.org/api/associations/?limit=25&offset=0&chr=1&chr=2&chr=3&mac=5&type=genic&significant=p</code><br />\
                Please refer to the detailed REST documentation for further information: <a target=_blank href=http://aragwas.1001genomes.org/docs/>AraGWAS Catalog REST API Documentation</a>"},
        ]


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
