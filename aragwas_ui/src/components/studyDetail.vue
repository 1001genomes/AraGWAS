<template>
    <div>
        <div class="banner-container" style="height: 80px">
            <div class="section" id="head">
                <div class="container">
                    <h4 class="white--text">
                        Study: {{ studyName }}
                    </h4>
                </div>
            </div>
            <v-parallax class="parallax-container" src="/static/img/ara2.jpg" height="80">
            </v-parallax>
        </div>
        <div class="container">
            <div class="row">
                <div class="col s12 m6">
                    <div class="row">
                        <br>
                        <div class="col s12"><h5>Description</h5></div>
                        <div class="col s12" id="description">{{ studyDescription }}</div>
                        <div class="col s12"><h5>Statistics</h5></div>
                        <div class="col s12" id="statistics">
                            <v-tabs
                                    id="mobile-tabs-1"
                                    grow
                                    scroll-bars
                                    :model="currentView"
                            >
                                <v-tab-item
                                        v-for="i in ['phenotypes','accessions']" :key="i"
                                        :href="'#' + i"
                                        ripple
                                        slot="activators"
                                        class="green lighten-1"
                                >
                                </v-tab-item>
                                <v-tab-content
                                        v-for="i in ['phenotypes','accessions']" :key="i"
                                        :id="i"
                                        slot="content"
                                >
                                    <v-card>
                                        <v-card-text>
                                            <div id="results" class="col s12"><br>
                                                <h5 class="brown-text center" v-if="n[currentView] === 0">No {{observed[currentView]}} found for query: {{queryTerm}}</h5>
                                                <table v-else>
                                                    <thead>
                                                    <tr>
                                                        <th v-for="key in columns[currentView]"
                                                            @click="sortBy(key)"
                                                            :class="{ active: sortKey == key }">
                                                            {{ key | capitalize }}
                                                        <span class="arrow" :class="sortOrders[currentView][key] > 0 ? 'asc' : 'dsc' ">
                                                        </span>
                                                        </th>
                                                    </tr>
                                                    </thead>
                                                    <tbody>
                                                    <tr v-for="entry in filteredData">
                                                        <td v-for="key in columns[currentView]">
                                                            {{entry[key]}}
                                                        </td>
                                                    </tr>
                                                    </tbody>
                                                </table>
                                            </div>
                                        </v-card-text>
                                    </v-card>
                                </v-tab-content>
                            </v-tabs>
                        </div>
                        <div id="to" class="col s12">
                            <div id="to_chart" class="chart"></div>
                        </div>
                        <div id="eo" class="col s12"><div class="chart" id="eo_chart"></div></div>
                        <div id="uo" class="col s12"><div class="chart" id="uo_chart"></div></div>
                    </div>
                    <div class="row">
                        <div class="col s12"><h5>Publications</h5></div>
                        <div class="col s12">
                        </div>
                    </div>
                </div>
                <div class="col s12 m6">
                    <br>
                    <table>
                        <thead>
                        <tr>
                            <th v-for="key in columns"
                                @click="sortBy(key)"
                                :class="{ active: sortKey == key }">
                                {{ key | capitalize }}
                                <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
                                </span>
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="entry in filteredData">
                            <td v-for="key in columns">
                                {{entry[key]}}
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="row">

            </div>
        </div>
    </div>
</template>

<script lang="ts">
    import Vue from 'vue'
    import {Component, Prop} from 'vue-property-decorator'

    @Component({
    })
    export default class StudyDetail extends Vue {
      @Prop
      studyId: string
      studyName: string = 'Test'
      studyDescription: string = 'A study conducted on n samples for phenotype p.'
      currentView: string = ''
      n = {'phenotypes': 0, 'accessions': 0}
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .banner-container {
        position: relative;
        overflow: hidden;
    }


    .parallax-container  {
        position:absolute;
        top:0;
        left:0;
        right:0;
        bottom:0;
        z-index:-1;
    }

    .container {
        margin:0 auto;
        max-width: 1280px;
        width: 90%
    }

    .banner-title h1 {
        font-size: 4.2rem;
        line-height: 110%;
        margin: 2.1rem 0 1.68rem 0;
    }
    .banner-subtext h5 {
        font-weight:300;
        color:black;
    }


    @media only screen and (min-width: 601px) {
        .container {
            width:85%
        }
    }

    @media only screen and (min-width: 993px) {
        .container {
            width:70%;
        }
    }

</style>
