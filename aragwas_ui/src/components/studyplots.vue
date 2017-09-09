<template>
    <v-tabs id="similar-tabs" grow scroll-bars v-model="currentViewIn">
        <v-tabs-bar>
            <v-tabs-item :href="'#' + i" ripple class="grey lighten-4 black--text"
                         v-for="i in ['On genes', 'On snp type']" :key="i">
                <div>{{ i }}</div>
            </v-tabs-item>
            <v-tabs-slider></v-tabs-slider>
        </v-tabs-bar>
        <v-tabs-items>
            <v-tabs-content :id="i" v-for="i in ['On genes', 'On snp type']" :key="i" class="pa-4" ref="plots">
                <div id="statistics" class="mt-2" v-if="i === 'On genes'" >
                    <vue-chart v-if="plotStatistics.topGenes.rows.length > 1" :columns="plotStatistics.topGenes.columns" :rows="plotStatistics.topGenes.rows" :options="{title: 'Distribution of significant associations on genes', legend: {position: 'none'}}" chart-type="BarChart" :chart-events="chartEvents"></vue-chart>
                    <h6 v-else style="text-align: center">Not enough significant hits</h6>
                </div>
                <div v-else>
                    <div v-if="plotStatistics.genic.rows.length>1">
                        <vue-chart v-if="_isSnpType" :columns="plotStatistics.genic.columns" :rows="plotStatistics.genic.rows" :options="{title: 'SNP type'}" chart-type="PieChart" ></vue-chart>
                        <vue-chart v-if="_isSnpType" :columns="plotStatistics.impact.columns" :rows="plotStatistics.impact.rows" :options="{title: 'SNP impact'}" chart-type="PieChart"></vue-chart>
                        <vue-chart v-if="_isSnpType" :columns="plotStatistics.annotation.columns" :rows="plotStatistics.annotation.rows" :options="{title: 'SNP annotation'}" chart-type="PieChart"></vue-chart>
                        <vue-chart :columns="plotStatistics.pvalueDistribution.columns" :rows="plotStatistics.pvalueDistribution.rows" :options="{title: 'Distribution of scores',legend: {position: 'none'}}" chart-type="ColumnChart"></vue-chart>
                        <vue-chart :columns="plotStatistics.mafDistribution.columns" :rows="plotStatistics.mafDistribution.rows" :options="{title: 'Distribution of MAF',legend: {position: 'none'}}" chart-type="ColumnChart"></vue-chart>
                        <vue-chart :show="false" :options="{width: width}" :columns="[]" :rows="[]"></vue-chart>
                    </div>
                    <h6 v-else style="text-align: center" >Not enough significant hits.</h6>
                </div>
            </v-tabs-content>
        </v-tabs-items>
    </v-tabs>
</template>

<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import _ from "lodash";

    @Component({
        name: "study-plots",
        props: ["plotStatistics"],
    })
    export default class StudyPlots extends Vue {
        @Prop()
        plotStatistics;

        currentViewIn: string = "On genes";

        width: number = 0;
        pieChartsRendered: boolean = false;

        debouncedOnResize = _.debounce(this.onResize, 300);

        chartEvents = {
            select: () => {
//                console.log(getSelection()[0]);
                },
        };

        // Get width-information for optimal re-rendering

        @Watch("currentViewIn")
        onCurrentViewChanged(newCurrentView) {
            if (newCurrentView === "On snp type") {
                this.pieChartsRendered = true;
            }
        }

        get _isSnpType() {
            return this.pieChartsRendered || this.currentViewIn === "On snp type";
        }

        onResize() {
            this.width = this.$el.offsetWidth;
        }
        beforeUpdate() {
            if( !(this.plotStatistics.topGenes.rows.length > 1) && this.plotStatistics.genic.rows.length>1){
                this.currentViewIn = "On snp type"
            }
        }
        mounted() {
            window.addEventListener('resize', this.debouncedOnResize);
            this.debouncedOnResize();
        }

    }
</script>
