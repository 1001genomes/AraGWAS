<template>
 <v-app fill-height footer toolbar id="app">
    <v-navigation-drawer disable-route-watcher temporary light overflow right v-model="drawer">
      <v-toolbar flat>
        <v-list>
          <v-list-tile> <span>Menu</span></v-list-tile>
        </v-list>
      </v-toolbar>
      <v-divider></v-divider>
      <v-list dense class="pt-0">
        <v-list-tile @click="starttour">
          <v-list-tile-content>
            <v-list-tile-title  ><span class="black--text">Take a tour?</span></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile :to="{path: '/faq'}">
          <v-list-tile-content>
            <v-list-tile-title ><span class="black--text">FAQ</span></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile :to="{path: '/about'}">
          <v-list-tile-content>
            <v-list-tile-title><span class="black--text">About</span></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile :to="{path: '/links'}">
          <v-list-tile-content>
            <v-list-tile-title><span class="black--text">Links</span></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile href="/docs" target="_blank">
          <v-list-tile-content>
            <v-list-tile-title><span>REST API documentation</span></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar class="white toolbar">
      <v-toolbar-title class="logo aragwas-logo"><router-link :to="{name: 'home'}">AraGWAS Catalog</router-link></v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-side-icon class="hidden-md-and-up" @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-items class="hidden-sm-and-down black--text">
          <v-btn flat class="links" @click="starttour"><span class="black--text">Take a tour?</span></v-btn>
          <v-btn flat class="links faq" id="faq-link" :to="{path: '/faq'}" ><span class="black--text">FAQ</span></v-btn>
          <v-btn flat class="links" id="about-link" :to="{path: '/about'}"><span class="black--text">About</span></v-btn>
          <v-btn flat class="links" id="links-link" :to="{path: '/links'}"><span class="black--text">Links</span></v-btn>
          <v-btn flat class="links" id="rest-link" href="/docs" target="_blank">REST API documentation</v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <main>
      <rotate-overlay v-if="rotateNotificationView"></rotate-overlay>
      <v-container fluid class="pa-0" >
        <router-view></router-view>
      </v-container>
    </main>
    <v-footer class="green" id="footer" >
      <div class="footer-text"  >
          AraGWAS is a public database for <em>Arabidopsis thaliana</em> GWAS studies.
        <div class="version hidden-sm-and-down">
          <ul>
            <li>{{versionInfo.version}}</li>
            <li>
              <a :href="versionInfo.buildUrl" target="_blank">{{versionInfo.build}}</a>
            </li>
            <li>
              <a :href="versionInfo.githubUrl+'/'+versionInfo.githash" target="_blank">{{versionInfo.githash}}</a>
            </li>
            <li><timeago :since="versionInfo.date" :auto-update="60"></timeago></li>
            <li>
                  <v-dialog v-model="dialog" scrollable>
                  <div slot="activator"><u>IMPRESSUM</u></div>
                  <v-card>
                      <v-card-title class="black--text">
                          <h3 class="headline mb-0">Impressum - Gregor Mendel Institute</h3>
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text class="black--text" style="height:400px">
                          <h5>Contact information</h5>
                          <div>GMI — Gregor-Mendel-Institut für Molekulare Pflanzenbiologie GmbH</div>
                          <div>Dr. Bohr-Gasse 3</div>
                          <div>1030 Vienna</div>
                          <div>Austria</div>
                          <div>T: +43 1 79044 9000</div>
                          <div>F: +43 1 79044 9001</div>
                          <div>E: office(at)gmi.oeaw.ac.at</div>
                          <br>

                          <h5>Legal information</h5>
                          <div>Type of business: Research Institute</div>
                          <div>Managing Director (Science): Dr Magnus Nordborg</div>
                          <div>Managing Director (Business): Dr Markus Kiess</div>
                          <div>Commercial register number: FN 203743y</div>
                          <div>Commercial register court: Vienna, Austria</div>
                          <div>Sales tax identification number: ATU51438706</div>
                          <div>The GMI is 100% owned by the Austrian Academy of Sciences</div>

                          <br>
                          <h5>Disclaimer</h5>
                          <div>This website provides information about research at the GMI. GMI makes no guarantees of accuracy, completeness and timeliness of the information on this website. The GMI, therefore, accepts no responsibility or liability for damages or losses resulting from the use of this website. The GMI provides links to other internet sites for the convenience of users. The GMI, its owners, managers, partners, and employees are not responsible for the availability or content of these external sites, nor do they endorse, warrant, or guarantee any commercial product, service, site, law firm, attorney or information described or offered at these other internet sites.
                          </div>
                          <br>
                          <h5>Privacy</h5>
                          <div>This website uses Google Analytics, a web analytics service provided by Google, Inc. (“Google”). Google Analytics uses “cookies”, which are text files placed on your computer, to help the website analyze how users use the site. The information generated by the cookie about your use of the website (including your anonymized IP address) will be transmitted to and stored by Google on servers in the United States. To perform the IP anonymization, Google will truncate/anonymize the last octet of the IP address for Member States of the European Union as well as for other parties to the Agreement on the European Economic Area. Google will use this information for the purpose of evaluating your use of the website, compiling reports on website activity for website operators and providing other services relating to website activity and internet usage. Google may also transfer this information to third parties where required to do so by law, or where such third parties process the information on Google's behalf. Google will not associate your anonymized IP address with any other data held by Google. You may refuse the use of cookies by selecting the appropriate settings on your browser, however please note that if you do this you may not be able to use the full functionality of this website. By using this website, you consent to the processing of data about you by Google in the manner and for the purposes set out above. Furthermore you can prevent Google’s collection and use of data (cookies and IP address) by downloading and installing the browser plug-in available <a href="https://tools.google.com/dlpage/gaoptout?hl=en">here</a></div>
                      </v-card-text>
                      <v-divider></v-divider>
                      <v-card-actions>
                          <v-btn class="green--text darken-1" flat="flat" @click="dialog = false">Agree</v-btn>
                      </v-card-actions>
                  </v-card>
              </v-dialog>
            </li>
          </ul>
        </div>
      </div>
    </v-footer>
  </v-app>
</template>

<script lang="ts">
  import Vue from "vue";
  import {Component} from "vue-property-decorator";
  import RotateOverlay from "./components/rotateOverlay.vue";

  import {loadApiVersion, loadStudies} from "./api";
  import ApiVersion from "./models/apiversion";

  @Component({
    components: {'rotate-overlay': RotateOverlay,},
  })
  export default class AppComponent extends Vue {
    versionInfo: ApiVersion = {} as ApiVersion;
    dialog = false;
    drawer = false;

    starttour(): void {
      this.$router.push({name:'home', query:{tour:'true'}})
    }

    get rotateNotificationView() {
      console.log(this.$route.name );
      const routeName = this.$route.name;
      return routeName == 'geneDetail' || routeName == 'map';
    }

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
  @import "../node_modules/intro.js/introjs.css";


  #main-content {
    padding-top:0;
    background-color:transparent;
  }
  .logo a {
    color:black;
    text-decoration:none;3em
    font-weight:300;
    font-size: 1em;
  }
  .links a {
      color:black;
      text-decoration:none;
  }
  .version {
    float:right;
    font-size: 0.85rem;
    text-transform: none;
  }
  .impressum {
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

  .footer-text {
    width:100%;
    font-size: 0.70em;
  }

  @media only screen and (min-width: 601px) {
    .footer-text {
        font-size:inherit;
    }
    .logo a {
      font-size: 2em;
    }
  }
  main
    position:relative;

  #app
    background-color: #fff;

  #footer
    color: #fff;

</style>
