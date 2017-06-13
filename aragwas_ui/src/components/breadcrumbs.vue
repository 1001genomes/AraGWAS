<template>
    <div>
        <v-breadcrumbs icons divider="chevron_right" class="left white--text" style="font-size: 24pt">
            <v-breadcrumbs-item
                    v-for="item in breadcrumbsItems" :key="item"
                    :disabled="item.disabled"
                    class="breadcrumbsitem"
                    :href="item.href"
                    router
            >
                <div v-if="detailvue">
                    <span :class="['title', {'green--text': !item.disabled}]">{{ item.text }}</span>
                </div>
                <div v-else>
                    <h4 v-if="item.disabled" class="grey--text text--lighten-2">{{ item.text }}</h4>
                    <h4 v-else class="white--text">{{ item.text }}</h4>
                </div>
            </v-breadcrumbs-item>
        </v-breadcrumbs>
        <v-divider></v-divider>
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
</style>
