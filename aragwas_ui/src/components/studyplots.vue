<template>
    <v-tabs id="similar-tabs" grow scroll-bars v-model="currentViewIn">
        <v-tabs-bar slot="activators">
            <v-tabs-slider></v-tabs-slider>
            <v-tabs-item :href="'#' + i" ripple class="grey lighten-4 black--text"
                         v-for="i in ['On genes', 'On snp type']" :key="i">
                <div>{{ i }}</div>
            </v-tabs-item>
        </v-tabs-bar>
        <v-tabs-content :id="i" v-for="i in ['On genes', 'On snp type']" :key="i" class="pa-4" ref="plots">
            <div id="statistics" class="mt-2" v-if="i === 'On genes'" >
                <vue-chart v-if="plotStatistics.topGenes.rows.length > 0" :columns="plotStatistics.topGenes.columns" :rows="plotStatistics.topGenes.rows" :options="{title: 'Distribution of significant associations on genes'}" chart-type="BarChart" :chart-events="chartEvents"></vue-chart>

            </div>
            <div v-else>
                <div v-if="plotStatistics.genic.rows.length>0">
                    <vue-chart :columns="plotStatistics.genic.columns" :rows="plotStatistics.genic.rows" :options="{title: 'SNP type'}" chart-type="PieChart"></vue-chart>
                    <vue-chart :columns="plotStatistics.impact.columns" :rows="plotStatistics.impact.rows" :options="{title: 'SNP impact'}" chart-type="PieChart"></vue-chart>
                    <vue-chart :columns="plotStatistics.annotation.columns" :rows="plotStatistics.annotation.rows" :options="{title: 'SNP impact'}" chart-type="PieChart"></vue-chart>
                    <vue-chart :columns="plotStatistics.pvalueDistribution.columns" :rows="plotStatistics.pvalueDistribution.rows" :options="{title: 'Distribution of scores'}" chart-type="ColumnChart"></vue-chart>
                    <vue-chart :columns="plotStatistics.mafDistribution.columns" :rows="plotStatistics.mafDistribution.rows" :options="{title: 'Distribution of MAF'}" chart-type="ColumnChart"></vue-chart>
                    <vue-chart :show="false" :options="{width: width}" :columns="[]" :rows="[]"></vue-chart>
                </div>
                <h6 v-else style="text-align: center" >No significant hits.</h6>
            </div>
        </v-tabs-content>
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
        selected;

        width: number = 0;

        debouncedOnResize = _.debounce(this.onResize, 300);

        chartEvents = {
            select: function() {
                var e = self.getSelection();
                alert('YEEEEAAAAAH! Nice selection! Gene:');
            },
        };

        // Re-name histograms distributions

        // Get width-information for optimal re-rendering

        onResize() {
            this.width = this.$el.offsetWidth;
//            this.$refs.chart.drawChart();
        }

        mounted() {
            window.addEventListener('resize', this.debouncedOnResize);
            this.debouncedOnResize();
        }

    }
</script>