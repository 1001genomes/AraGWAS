<template>
 <v-app top-toolbar footer>
    <v-toolbar class="white toolbar">
      <v-toolbar-logo class="logo"><router-link to="/">AraGWAS</router-link></v-toolbar-logo>
      <v-toolbar-items class="black--text">
        <v-toolbar-item><span class="black--text">Submit GWAS Study</span></v-toolbar-item>
          <v-toolbar-item><span class="black--text">Take a tour?</span></v-toolbar-item>
          <v-toolbar-item><span class="black--text">FAQ & Tutorials</span></v-toolbar-item>
      </v-toolbar-items>
    </v-toolbar>
    <main>
      <v-content id="main-content">
        <v-container fluid>
          <router-view></router-view>
        </v-container>
      </v-content>
    </main>
    <v-footer class="green lighten-1" >
      <div >
        AraGWAS is a public database for Arabidopsis thaliana GWAS studies.
      </div>
    </v-footer>
  </v-app>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';

  @Component({})
  export default class AppComponent extends Vue {

  }
</script>

<style lang="stylus">
  @import '~vuetify/src/stylus/main'
  $theme.primary = $red.darken-2
  @import './assets/css/main.css'
  @import './assets/css/animate.css'

  #main-content {
    padding-top:0;
    background-color:transparent;
  }
  .logo a {
    color:black;
    text-decoration:none;
    font-weight:300;
  }

</style>
