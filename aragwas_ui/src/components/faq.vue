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
                <v-card class="mt-3"  v-for="faq in faqs" :key="faq">
                    <h5 class="pl-4 pt-3 pr-4 green--text text--darken-2">
                        {{ faq.question }}
                    </h5>
                    <v-divider/>
                    <div style="font-size: 12pt;" class="pl-4 pt-3 pr-4 black--text">
                        {{ faq.answer }}
                    </div>
                    <br>
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
    export default class FAQ extends Vue {
        breadcrumbs = [{text: "Home", href: "/"}, {text: "FAQs", href: "/faq", disabled: true}];
        faqs = [
            {question: "Why?",
                answer: "Because!!"},
            {question: "Why did you recompute all the GWASs?",
                answer: "We wanted to provide you with truly comparable data, and to ensure that across different published results, we needed to generate results using a standardized method."},
            {question: "What standardized method did you use to generate the results?",
                answer: "The provided p-values and association results were obtained using a mixed linear model (via the EMMAX algorithm) on boxcox corrected phenotype data."},
        ]
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
