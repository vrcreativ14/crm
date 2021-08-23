<template>
    <div>
        <div v-if="state === 'loading-trims'">
            Loading trim options...
        </div>
        <div v-if="state === 'awaiting-trim-selection'">
            Please select a trim
            <select name="selected-trim" @change="userSelectedTrim()" v-model="selectedTrim">
                <option :value="null" disabled>Select a trim</option>

                <option v-bind:value="trim" v-for="trim of trims">
                    {{trim.title}}
                </option>
            </select>
        </div>
        <div v-if="state === 'error'" class="text-danger">
            {{ errorMessage }}
        </div>
    </div>
</template>

<script>
export default {
    name: "select-trim",
    props: ["vehicleInfo"],
    data() {
        return {
            state: "loading-trims",
            trims: [],
            selectedTrim: null,
            errorMessage: ""
        };
    },
    methods: {
        userSelectedTrim() {
            if (this.selectedTrim !== null) {
                this.$emit('trim-selected', this.selectedTrim);
            }
        }
    },
    mounted() {
        $.get(qicTrimsUrl, this.vehicleInfo)
                .done((response) => {
                    this.$nextTick(() => {
                        this.state = "awaiting-trim-selection";
                        this.trims = response.trims;
                    });
                })
                .fail((xhr) => {
                    this.$nextTick(() => {
                        this.state = "error";
                        this.errorMessage = xhr.responseText;
                    });
                });
    }
}
</script>

<style scoped>
select {
    width: 100%;
}
</style>