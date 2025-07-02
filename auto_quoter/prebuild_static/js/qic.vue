<template>
    <div>
        <div v-if="state === 'input-chassis-number'">
            <chassis-number-input :initial-chassis-number="initialChassisNumber"
                                  @car-info-loaded="handleCarInfoLoaded"></chassis-number-input>
        </div>
        <div v-if="state === 'select-trim'">
            <select-trim :vehicle-info="vehicleInfo" @trim-selected="handleTrimSelected"></select-trim>
        </div>
        <div v-if="state === 'get-quotes'">
            <get-quotes :vehicle-info="vehicleInfo" :selected-trim="selectedTrim"></get-quotes>
        </div>
        <a href="#" @click.prevent="previousStep()" v-if="state !== 'input-chassis-number'">&lt; Previous Step</a>
    </div>
</template>

<script>
import ChassisNumberInput from './qic_components/1.chassis_number_input.vue';
import SelectTrim from './qic_components/2.select_trim.vue';
import GetQuotes from './qic_components/3.get_quotes.vue';

export default {
    components: {
        ChassisNumberInput,
        SelectTrim,
        GetQuotes
    },
    data: function () {
        return {
            initialChassisNumber: window.qicAutoQuoterInitialData.chassisNumber,
            state: "input-chassis-number",
            vehicleInfo: null,
            selectedTrim: null,
        };
    },
    methods: {
        handleCarInfoLoaded(vehicleInfo) {
            this.state = 'select-trim';
            this.vehicleInfo = vehicleInfo;
        },
        handleTrimSelected(trimInfo) {
            this.state = 'get-quotes';
            this.selectedTrim = trimInfo;
        },
        previousStep() {
            if (this.state === 'get-quotes') {
                this.selectedTrim = null;
                this.state = 'select-trim';
            } else if (this.state === 'select-trim') {
                this.vehicleInfo = null;
                this.state = 'input-chassis-number';
            }
        }
    },
    mounted() {
        $("#calculate-premiums").hide();
        $(".show-insurer-modal").on('click', () => {
            this.$destroy();
            $(".show-insurer-modal").off('click');
        });
    },
    destroyed() {
        $("#calculate-premiums").show();
    }
}
</script>