<template>
    <v-select
        :items="genes"
        v-model="selectedItem"
        label="Search for a gene..."
        dark
        hint="Type gene ID (i.e. AT1G12) or synonym (i.e. FLC)"
        prepend-icon="search"
        max-height="auto"
        autocomplete
        item-value="id"
        item-text="name"
        @input.native="changeQueryTerm"
        return-object
    ></v-select>
</template>
<script lang="ts">
    import Vue from "vue";
    import {Component, Model, Prop, Watch} from "vue-property-decorator";

    import {autoCompleteGenes} from "../api";
    import Gene from "../models/gene";

    @Component({})
    export default class GeneSearch extends Vue {
        genes: Gene[] = [];
        @Model("selected")
        @Prop()
        selectedGene: Gene;
        selectedItem: Gene | null = null;
        searchTerm: string = "";

        @Watch("searchTerm")
        async onSearchValueChanged(val, oldVal) {
            this.genes = await(autoCompleteGenes(val));
        }

        @Watch("selectedItem")
        onItemSelected(val, oldVal) {
            this.$emit("selected", val);
        }

        @Watch("selectedGene")
        async onSelectedGeneChanged(val: Gene, oldVal: Gene) {
            if (!this.isGeneInAvailableList(val)) {
                this.genes = [val];
            }
            this.selectedItem = val;
        }

        changeQueryTerm(event) {
            this.searchTerm = event.target.value;
        }

        isGeneInAvailableList(gene: Gene): boolean {
            if (this.genes.length === 0 || gene === null) {
                return false;
            }
            return (this.genes.filter( (d) => d.id === gene.id)).length > 0;
        }
    }
</script>
<style scoped>

</style>