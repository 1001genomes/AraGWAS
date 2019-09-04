<template>
  <div>
    <div class="chart-wrapper" id="chart-distro1" ref="chartWrapper"></div>
    <!--Sorry about all the inline JS. It is a quick way to show what options are available-->
    <div class="chart-options">
      <p>Show:</p>
       <v-btn class="btn--small icon--left green lighten-1" light @click="showBoxPlot">
          Box Plot
      </v-btn>
      <v-btn class="btn--small icon--left green lighten-1" light @click="showNotchedBoxPlot">
          Notched Box Plot
      </v-btn>
      <v-btn class="btn--small icon--left green lighten-1" light @click="showViolinUnboundPlot">
          Violin Plot Unbound
      </v-btn>
      <v-btn class="btn--small icon--left green lighten-1" light @click="showViolinClampPlot">
          Violin Plot Clamp to Data
      </v-btn>
      <v-btn class="btn--small icon--left green lighten-1" light @click="showBeanPlot">
          Bean Plot
      </v-btn>
      <v-btn class="btn--small icon--left green lighten-1" light @click="showBeeswarmPlot">
          Beeswarm Plot
      </v-btn>
      <v-btn class="btn--small icon--left green lighten-1" light @click="showScatterPlot">
         Scatter Plot
      </v-btn>
      <v-checkbox v-model="showTrendLines" primary label="Show trend" value="1" class="mb-0" hide-details></v-checkbox>
    </div>
  </div>
</template>
<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import { Component, Prop, Watch } from "vue-property-decorator";
    import _ from "lodash";
    import distrochart from "../viz/distrochart.js";
    import Accession from "../models/accession";

    @Component({
        name: "distro-chart",
        filters: {
            round: function(value) {
            return Math.round(value * 100) / 100;
            }
        }
    })
    export default class DistroChart extends Vue {
      @Prop({type: null})
      data: any;
      readonly maxHeight: number = 800;

      distrochart = distrochart() as any;
      chart ;
      showTrendLines: boolean = false;
      debouncedOnResize = _.debounce(this.onResize, 300);
      debouncedDrawPlot = _.debounce(this.drawPlot, 300);
      debounceUpdateData = _.debounce(this.updateData, 300);
      width: number = 400;
      height: number = 400;

       mounted() {
          window.addEventListener('resize', this.debouncedOnResize);
          this.debounceUpdateData();
      }

      onResize(): void {
          const chartComponent = this.$refs.chartWrapper as HTMLElement;
          if (chartComponent == null)
            return;
            if (this.$el.offsetWidth == 0 ||chartComponent.offsetHeight ==0 ) {
              return;
            }
            this.width = this.$el.offsetWidth
            this.height = chartComponent.offsetHeight;
             Vue.nextTick(() => {
              this.debouncedDrawPlot();
             });
      }

      drawPlot(): void {
        if (this.chart == null) {
          return;
        }
        d3.select(this.chart.settings.selector)
                .style("max-width", this.width + "px");
        const chartComponent = this.$refs.chartWrapper as HTMLElement;
        if (chartComponent != null) {
          if (this.maxHeight < chartComponent.offsetHeight) {
            this.height = chartComponent.offsetHeight;
          } else {
            this.height = this.maxHeight;
          }

        }
        this.chart.settings.chartSize.height = this.height;
        this.chart.settings.chartSize.width = this.width;
        this.chart.divWidth = this.chart.settings.chartSize.width;
        this.chart.divHeight = this.chart.settings.chartSize.height;
        this.chart.width = this.chart.divWidth - this.chart.margin.left - this.chart.margin.right;
        this.chart.height = this.chart.divHeight - this.chart.margin.top - this.chart.margin.bottom;

        this.chart.update();
        this.chart.boxPlots.update();
      }


      hideAllPlots(): void {
        this.chart.dataPlots.change({showPlot:false,showBeanLines:false});
        this.chart.violinPlots.hide();
        this.chart.notchBoxes.hide();
        this.chart.boxPlots.hide();
      }

      @Watch("data")
      onDataChanged(data) {
        this.debounceUpdateData();
      }

      updateData(): void {
         d3.select("#chart-distro1").selectAll("*").remove();
         if (! this.data) {
           return;
         }
         this.chart = this.distrochart({
            data: this.data,
            xName: 'label',
            yName: 'value',
            axisLabels: {xAxis: null, yAxis: 'Values'},
            selector: "#chart-distro1",
            chartSize:{height:this.height, width:this.width}, constrainExtremes:true});
          if (this.chart != null) {
            this.chart.renderBoxPlot();
            this.chart.renderDataPlots();
            this.chart.renderNotchBoxes({showNotchBox:false});
            this.chart.renderViolinPlot({showViolinPlot:false});
          }
          this.debouncedOnResize()
      }


      @Watch("showTrendLines")
      onChangeTrendLine(val: boolean, oldVal: boolean): void {
        if(val){
          this. chart.dataPlots.change({showLines:['median','quartile1','quartile3']});
         } else {
           this.chart.dataPlots.change({showLines: false});
        }
      }

      showBoxPlot(): void {
        this.hideAllPlots();
        this.chart.boxPlots.show({reset: true});
      }
      showNotchedBoxPlot(): void {
        this.hideAllPlots();
        this.chart.boxPlots.show({reset: true, showBox: false,showOutliers: true, boxWidth: 20, scatterOutliers: true});
        this.chart.notchBoxes.show({reset: true});
      }

      showViolinUnboundPlot(): void {
        this.hideAllPlots();
        this.chart.violinPlots.show({reset: true, clamp: 0});
        this.chart.boxPlots.show({reset:true, showWhiskers:false,showOutliers:false,boxWidth:10,lineWidth:15,colors:['#555']});
      }
      showViolinClampPlot(): void {
        this.hideAllPlots();
        this.chart.violinPlots.show({reset: true, clamp: 1});
        this.chart.boxPlots.show({reset:true, showWhiskers:false,showOutliers:false,boxWidth:10,lineWidth:15,colors:['#555']});
      }

      showBeanPlot(): void {
        this.hideAllPlots();
        this.chart.violinPlots.show({reset:true, width:75, clamp:0, resolution:30, bandwidth:50});
        this.chart.dataPlots.show({showBeanLines:true,beanWidth:15,showPlot:false,colors:['#555']});
      }
      showBeeswarmPlot(): void {
        this.hideAllPlots();
        this.chart.dataPlots.show({showPlot:true, plotType:'beeswarm',showBeanLines:false, colors:null});
      }
       showScatterPlot(): void {
         this.hideAllPlots();
        this.chart.dataPlots.show({showPlot:true, plotType:40, showBeanLines:false,colors:null});
      }


    }
</script>
<style lang="stylus">
/* Primary Chart */
/* Nested divs for responsiveness */
.chart-wrapper {
  //max-width: 800px; /* Overwritten by the JS */
  min-width: 304px;
  max-height: 800px;
  min-height:304px;
  height:100%;
  margin-bottom: 8px;
  background-color: #FAF7F7;
}

.chart-wrapper .inner-wrapper {
  position: relative;
  padding-bottom: 50%; /* Overwritten by the JS */
  width: 100%;
}

.chart-wrapper .outer-box {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}

.chart-wrapper .inner-box {
  width: 100%;
  height: 100%;
}

.chart-wrapper text {
  font-family: sans-serif;
  font-size: 13px;
}

.chart-wrapper .axis path, .chart-wrapper .axis line {
  fill: none;
  stroke: #888;
  stroke-width: 2px;
  shape-rendering: crispEdges;
}

.chart-wrapper .y.axis .tick line {
  stroke: lightgrey;
  opacity: 0.6;
  stroke-dasharray: 2, 1;
  stroke-width: 1;
  shape-rendering: crispEdges;
}

.chart-wrapper .x.axis .domain {
  display: none;
}

.chart-wrapper div.tooltip {
  position: absolute;
  text-align: left;
  padding: 3px;
  font: 12px sans-serif;
  background: lightcyan;
  border: 0px;
  border-radius: 1px;
  pointer-events: none;
  opacity: 0.7;
}

/* Box Plot */
.chart-wrapper .box-plot .box {
  fill-opacity: 0.4;
  stroke-width: 2;
}

.chart-wrapper .box-plot line {
  stroke-width: 2px;
}

.chart-wrapper .box-plot circle {
  fill: white;
  stroke: black;
}

.chart-wrapper .box-plot .median {
  stroke: black;
}

.chart-wrapper .box-plot circle.median {
  /* the script makes the circles the same color as the box, you can override this in the js */
  fill: white !important;
}

.chart-wrapper .box-plot .mean {
  stroke: white;
  stroke-dasharray: 2, 1;
  stroke-width: 1px;
}

@media (max-width: 500px) {
  .chart-wrapper .box-plot circle {
    display: none;
  }
}

/* Violin Plot */
.chart-wrapper .violin-plot .area {
  shape-rendering: geometricPrecision;
  opacity: 0.4;
}

.chart-wrapper .violin-plot .line {
  fill: none;
  stroke-width: 2px;
  shape-rendering: geometricPrecision;
}

/* Notch Plot */
.chart-wrapper .notch-plot .notch {
  fill-opacity: 0.4;
  stroke-width: 2;
}

/* Point Plots */
.chart-wrapper .points-plot .point {
  stroke: black;
  stroke-width: 1px;
}

.chart-wrapper .metrics-lines {
  stroke-width: 4px;
}

/* Non-Chart Styles for demo */
.chart-options {
  min-width: 200px;
  font-size: 13px;
  font-family: sans-serif;
  margin-top:50px;
}

.chart-options button {
  margin: 3px;
  padding: 3px;
  font-size: 12px;
}

.chart-options p {
  display: inline;
}

@media (max-width: 500px) {
  .chart-options p {
    display: block;
  }
}
</style>
