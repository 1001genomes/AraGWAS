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
                <v-layout>
                    <v-flex xs12 column>
                        <h5 class="light"><v-icon class="green--text" style="font-size:30px">info</v-icon> What is AraGWASCatalog?</h5>
                        <p class="light">The AraGWASCatalog is a central, standardised, quality controlled and manually curated repository for genome-wide association studies (GWAS) for the model organism <i>Arabidopsis thaliana</i>.</p>
                    </v-flex>
                </v-layout>
                <v-layout>
                    <v-flex xs12 column>
                        <h5 class="light"><v-icon class="green--text" style="font-size:30px">people</v-icon> People behind AraGWASCatalog</h5>
                        <v-card class="mt-2 mb-4">
                            <v-card-text>
                                <div class="waves-effect waves-block waves-light">
                                    <a target="_blank" href="http://www.cctb.uni-wuerzburg.de/groups/evolutionary_genomics_korte/people/">
                                        <img style="height:80px;padding:5px 5px;" class="activator" src="/static/img/cctb_logo.png">
                                    </a>
                                </div>
                                <div  class="card-content">
                                    <h5 class="light grey--text text--darken-4">University of Würzburg, Center for Computational and Theoretical Biology</h5>
                                    <p><a target="_blank" href="http://www.cctb.uni-wuerzburg.de/groups/evolutionary_genomics_korte/people/">JProf. Dr. Arthur Korte</a>
                                        <a href="mailto:arthur.korte@uni-wuerzburg.de" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                        <v-card class="mt-2 mb-4">
                            <v-card-text>
                                <div class="waves-effect waves-block waves-light">
                                    <a target="_blank" href="https://bit.cs.tum.de">
                                        <img style="height:60px;padding:5px 5px;" class="activator" src="/static/img/tumcs_logo.png">
                                    </a>
                                    </br>
                                    <a target="_blank" href="https://bit.cs.tum.de">
                                        <img style="height:60px;padding:5px 5px;" class="activator" src="/static/img/hswt_logo.png">
                                    </a>
                                </div>
                                <div  class="card-content">
                                    <h5 class="light grey--text text--darken-4">TUM Campus Straubing for Biotechnology and Sustainability</h5>
                                    <h5 class="light grey--text text--darken-4">Weihenstephan-Triesdorf University of Applied Sciences</h5>
                                    <p><a target="_blank" href="https://www.bsse.ethz.ch/mlcb">Prof. Dr. Dominik Grimm</a>
                                        <a href="mailto:dominik.grimm@bsse.ethz.ch" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                        <v-card class="mt-2 mb-4">
                            <v-card-text>
                                <div class="waves-effect waves-block waves-light">
                                    <a target="_blank" href="https://www.bsse.ethz.ch/mlcb">
                                        <img style="height:60px;padding:5px 5px;" class="activator" src="/static/img/eth_logo.png">
                                    </a>
                                </div>
                                <div  class="card-content">
                                    <h5 class="light grey--text text--darken-4">ETH Zürich, Department for Biosystems Science and Engineering</h5>
                                    <p><a target="_blank" href="https://www.bsse.ethz.ch/mlcb">Prof. Dr. Karsten Borgwardt</a>
                                        <a href="mailto:karsten.borgwardt@bsse.ethz.ch" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                    <p><a target="_blank" href="https://www.bsse.ethz.ch/mlcb">Matteo Togninalli</a>
                                        <a href="mailto:matteo.togninalli@bsse.ethz.ch" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                        <v-card class="mt-2 mb-4">
                            <v-card-text>
                                <div class="waves-effect waves-block waves-light">
                                    <a target="_blank" href="https://www.gmi.oeaw.ac.at/research-groups/magnus-nordborg/">
                                        <img style="height:80px;padding:5px 5px;" class="activator" src="/static/img/GMI_logo.png">
                                    </a>
                                </div>
                                <div class="card-content">
                                    <h5 class="light grey--text text--darken-4">Gregor Mendel Institute of Molecular Plant Biology</h5>
                                    <p><a target="_blank" href="https://www.gmi.oeaw.ac.at/research-groups/magnus-nordborg/">Prof. Dr. Magnus Nordborg</a>
                                        <a href="mailto:magnus.nordborg@gmi.oeaw.ac.at" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                    <p><a target="_blank" href="https://www.gmi.oeaw.ac.at/research-groups/magnus-nordborg/">Ümit Seren</a>
                                        <a href="mailto:uemit.seren@gmi.oeaw.ac.at" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                        <v-card class="mt-2 mb-4">
                            <v-card-text>
                                <div class="waves-effect waves-block waves-light">
                                    <a target="_blank" href="http://www.weigelworld.org/">
                                        <img style="height:120px;padding:5px 5px;" class="activator" src="/static/img/mpi_logo.png">
                                    </a>
                                </div>
                                <div class="card-content">
                                    <h5 class="light grey--text text--darken-4">Max Planck Institute for Developmental Biology</h5>
                                    <p><a target="_blank" href="http://www.weigelworld.org/">Prof. Dr. Detlef Weigel</a>
                                        <a href="mailto:weigel@tue.mpg.de" target="_top"><v-icon class="green--text">email</v-icon></a>
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-flex>
                </v-layout>
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
        breadcrumbs = [{text: "Home", href: "/"}, {text: "About", href: "/about", disabled: true}];
    }

</script>

<style scoped>

</style>
