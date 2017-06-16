<template>
    <div class="mt-0">
        <v-parallax class="parallax-container" src="/static/img/ara5.jpg" height="80">
            <div class="section">
                <div class="container mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                </div>
            </div>
        </v-parallax>
        <div class="container">
            <div class="section">
                <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields"></top-associations>
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

    @Component({
        components: {
            "breadcrumbs": Breadcrumbs,
            "top-associations": TopAssociationsComponent,
        },
    })
    export default class TopAssociations extends Vue {
        loading: boolean = false;
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Top Associations", href: "#/top-associations", disabled: true}];
        maf = ["1", "1-5", "5-10", "10"];
        chr = ["1", "2", "3", "4", "5"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        hideFields = ["name"];
        filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, type: this.type};
        showControls = ["maf","chr","annotation","type"]
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .section {
        padding-top: 1rem;
    }
</style>
