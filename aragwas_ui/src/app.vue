<template>
 <v-app>
    <v-toolbar class="white toolbar">
      <v-toolbar-logo class="logo"><router-link :to="{path: '/', props: { currentView: '', queryTerm: '', currentPage: 1 }}">Ara<b>GWAS</b>Catalog</router-link></v-toolbar-logo>
      <v-toolbar-items class="black--text">
          <v-toolbar-item><span class="black--text">Take a tour?</span></v-toolbar-item>
          <v-toolbar-item><span class="black--text">FAQ & Tutorials</span></v-toolbar-item>
      </v-toolbar-items>
    </v-toolbar>
    <main>
      <v-container fluid class="pa-0">
        <router-view></router-view>
      </v-container>
    </main>
    <v-footer class="green" >
      <div >
          AraGWAS is a public database for <em>Arabidopsis thaliana</em> GWAS studies.
        <div class="version">
          <ul>
            <li>{{versionInfo.version}}</li>
            <li>
              <a :href="versionInfo.build_url" target="_blank">{{versionInfo.build}}</a>
            </li>
            <li>
              <a :href="versionInfo.github_url" target="_blank">{{versionInfo.githash}}</a>
            </li>
            <li><timeago :since="versionInfo.date" :auto-update="60"></timeago></li>
          </ul>
        </div>
      </div>
    </v-footer>
  </v-app>
</template>

<script lang="ts">
  import Vue from "vue";
  import Component from "vue-class-component";

  import {loadApiVersion, loadStudies} from "./api";
  import ApiVersion from "./models/apiversion";

  @Component({})
  export default class AppComponent extends Vue {
    versionInfo: ApiVersion = {} as ApiVersion;

    async created() {
      const data: ApiVersion = await loadApiVersion();
      this.versionInfo = data;
    }
  }
</script>

<style lang="stylus">
  @import "./assets/css/main.css"
  @import "./assets/css/animate.css"
  @import "./stylus/main"

  #main-content {
    padding-top:0;
    background-color:transparent;
  }
  .logo a {
    color:black;
    text-decoration:none;
    font-weight:300;
  }
  .version {
    float:right;
    font-size: 0.85rem;
    text-transform: none;
  }
  .version a {
    color:#fff;
  }
  .version ul {
    list-style: none;
    margin: 0;
    padding: 0;

  }
  .version ul li {
    display: inline-block;
    padding: 2px;
  }

</style>
