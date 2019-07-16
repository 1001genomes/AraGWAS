<template>
    <div>
        <v-breadcrumbs icons divider="chevron_right" class="left white--text" >
            <v-breadcrumbs-item
                    v-for="item in breadcrumbsItems" :key="item.text"
                    :disabled="item.disabled"
                    class="breadcrumbsitem"
                    :to="item.href"
                    exact

            >
                <div v-if="detailvue">
                    <span :class="[ {'green--text': !item.disabled}]">{{ item.text }}</span>
                </div>
                <div v-else>
                    <h4 v-if="item.disabled" class="grey--text text--lighten-2">{{ item.text }}</h4>
                    <h4 v-else class="white--text">{{ item.text }}</h4>
                </div>
            </v-breadcrumbs-item>
        </v-breadcrumbs>
    </div>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Prop} from "vue-property-decorator";

    import Router from "../router";

    @Component({
        name: 'breadcrumbs',
        props: ['breadcrumbsItems'],
    })
    export default class Breadcrumbs extends Vue {
      @Prop()
      breadcrumbsItems: [{}];
      router = Router;
      detailvue = false;
      mounted() {
          if (this.breadcrumbsItems.length > 2) {
            this.detailvue = true;
          }
      }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

ul.breadcrumbs {
    padding-left:0px;
}
.breadcrumbsitem {
    font-size:1em;
}
.breadcrumbsitem h4 {
    font-size:20px;
}

@media only screen and (min-width: 601px) {
    .breadcrumbsitem {
        font-size:32px;
    }
    .breadcrumbsitem span  {
        font-size:24px;
    }
    .breadcrumbsitem h4 {
        font-size:34px;
    }

}


</style>
