<template>
    <div class="mt-0">
        <v-parallax class="parallax-container" src="/static/img/ara2.jpg" height="80">
            <div class="section">
                <div class="breadcrumbs-container mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                </div>
            </div>
        </v-parallax>
        <div class="page-container">
            <div class="section">
                <v-layout row class="mb-4">
                    <v-flex xs12><h5 class="mb-2 mt-3"><v-icon class="green--text lighten-1" style="vertical-align: middle;">trending_up</v-icon> Top Associations</h5><v-divider class="mb-3"></v-divider>
                        <span style="font-size: 1.2rem">Check out the top hits across the <em>Arabidopsis thaliana</em> genome. This table shows all top associations (sorted by score, i.e. - log<sub>10</sub>(p-value)) that are stored in the database. Significant associations are marked in blue.</span></v-flex>
                </v-layout>
                <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields" :view="{name: 'top-associations'}" :highlightedAssociation="test"></top-associations>
            </div>
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch} from "vue-property-decorator";

    import {loadTopAssociations} from "../api";
    import Page from "../models/page";
    import Study from "../models/study";
    import Breadcrumbs from "./breadcrumbs.vue"
    import TopAssociationsComponent from "./topasso.vue"

    import tourMixin from "../mixins/tour.js";

    @Component({
        components: {
            "breadcrumbs": Breadcrumbs,
            "top-associations": TopAssociationsComponent,
        },
        mixins: [tourMixin],
    })
    export default class TopAssociations extends Vue {
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Top Associations", href: "#/top-associations", disabled: true}];
        maf = ["1","1-5","5-10", "10"];
        mac = ["5"];
        chr = ["1", "2", "3", "4", "5"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        hideFields = [];
        filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, mac: this.mac, type: this.type};
        showControls = ["maf","chr","annotation","type","mac"];
        test = 'chr2:122242';

        tourOptions = {
            steps: [
                {
                    element: ".association-table-container",
                    intro: "This table shows all top associations (sorted by score, i.e. -log10(p-value)) that are stored in the database. Significant associations are marked in blue.",
                    position: "left"
                },
                {
                    element: ".associations-control-container",
                    intro: "You can use these filters to filter the top associations list",
                    position: "right"
                }
            ],
            nextPage: {name: "geneDetail", params:{geneId: "AT1G54180"}}
        };
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
