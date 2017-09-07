<template>
    <div id="rotate">
        <div>
            <i class="material-icons">screen_rotation</i>
        </div>
    </div>
</template>
<script lang="ts">
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    @Component({
        name: "rotate-overlay",
        filters: {
            round: function(value) {
                return Math.round(value * 100)/ 100;
            }
        }
    })
    export default class RotateOverlay extends Vue {

    }
</script>
<style lang="stylus">
    #rotate
        display: none;
        div
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            i.material-icons
                color:white;
                font-size:3em;
                position:fixed;
                top: calc(50% - 42px);


    @media only screen and (max-device-width: 479px) and (orientation: portrait) {
        #rotate {
            background-color: #303030;
            opacity: 0.9;
            display: block;
            height: 100%;
            width: 100%;
            top:0;
            left:0;
            position: absolute;
            z-index:9999;
        }
    }
</style>