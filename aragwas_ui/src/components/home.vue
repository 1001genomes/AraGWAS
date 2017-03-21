<template>
  <div>
    <div class="banner-container white--text" style="height:420px">
      <div class="container">
        <div class="banner-title">
          <br>
          <h1 class="white--text text-xs-center">AraGWAS</h1>
        </div>
        <div class="banner-subtext">
          <h5 class="light text-xs-center">AraGWAS is a public database catalog of <em>Arabidopsis thaliana</em> associations from published GWAS studies.</h5>
          <br>
          <h5 class="light text-xs-center">This Database allows to search and filter for public GWAS studies and associations and to obtain additional meta-information.</h5>
        </div>
        <div>Autocomplete</div>
      </div>
      <v-parallax class="parallax-container" src="/static/img/ara1.jpg" height="420">
      </v-parallax>
    </div>
    <div class="section mt-4">
      <div class="container">
        <v-row class="text-xs-center">
          <v-col xs12 md6 lg3>
            <div class="icon-block">
                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">view_list</i></h3>
                <h5 class="text-xs-center">Public GWAS studies</h5>
                <p class="light justify">Browse through all available public <em>Arabidopsis thaliana</em> GWAS studies.</p>
                <router-link class="btn btn--large icon--left green lighten-1" to="/studies"><v-icon left>view_list</v-icon> GWAS studies</router-link>
            </div>
          </v-col>
          <v-col xs12 md6 lg3>
            <div class="icon-block">
                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">code</i></h3>
                <h5 class="text-xs-center">REST API</h5>
                <p class="light justify">The REST API can be used to retrieve associations and meta-information from AraGWAS via URLs.</p>
                <router-link class="btn btn--large icon--left green lighten-1" to="/faq/rest"><v-icon left>code</v-icon> REST API</router-link>
            </div>
          </v-col>
          <v-col xs12 md6 lg3>
            <div class="icon-block">
                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">rowing</i></h3>
                <h5 class="text-xs-center">Take a Tour</h5>
                <p class="light justify">Take a guided tour through AraGWAS and familiarise yourself with all available public functions.</p>
                <a class="btn btn--large icon--left green lighten-1"><v-icon left>rowing</v-icon>GWAS studies</a>
            </div>
          </v-col>
          <v-col xs12 md6 lg3>
            <div class="icon-block">
                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">backup</i></h3>
                <h5 class="text-xs-center">FAQ &amp; Tutorials</h5>
                <p class="light justify">Here, you can find detailed help about the functions of AraGWAS, its integrated data and frequently asked questions.</p>
                <router-link class="btn btn--large icon--left green lighten-1" to="/faq"><v-icon left>help_outline</v-icon> FAQ</router-link>
            </div>
          </v-col>
        </v-row>
        <v-row class="text-xs-center">
          <v-spacer></v-spacer>
          <v-col xs12 md6 lg3>
            <div class="icon-block">
                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">backup</i></h3>
                <h5 class="text-xs-center">Submit GWAS study</h5>
                <p class="light justify">Submit and publish your own GWAS study in order to share it with the community</p>
                <router-link class="btn btn--large icon--left green lighten-1" to="/submission"><v-icon left>backup</v-icon> Submit GWAS study</router-link>
            </div>
          </v-col>
          <v-spacer></v-spacer>
        </v-row>
      </div>
    </div>
    <div class="banner-container white--text mt-5" style="height:300px">
      <v-parallax class="parallax-container" src="/static/img/ara3.jpg" height="300">
      </v-parallax>
    </div>
    <div class="container mt-5 mb-5">
        <div class="section">
          <v-row>
            <v-col xs12 >
                <h5 class="light"><v-icon class="green--text lighten-1">fiber_new</v-icon> News &amp; Updates</h5>
                <v-card>
                  <v-card-text>
                    <div><v-icon class="green--text lighten-1">fiber_new</v-icon> AraGWAS is online</div>
                    <div>
                      <p class="light">
                            We are proud to announce that the first public GWAS catalogue for the model organism <em>Arabidopsis thaliana</em> has launched.
                      </p>
                    </div>
                  </v-card-text>
                </v-card>
            </v-col>
          </v-row>
        </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue'
  import Component from 'vue-class-component'

  @Component({
  })
  export default class Home extends Vue {

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

  .banner-title {

  }

  .banner-title h1 {
    font-size: 4.2rem;
    line-height: 110%;
    margin: 2.1rem 0 1.68rem 0;
  }

  .banner-subtext {

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
