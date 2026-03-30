package com.waste.helper.domain;

import static com.waste.helper.domain.DisposalGuideTestSamples.*;
import static com.waste.helper.domain.FavoriteRegionTestSamples.*;
import static com.waste.helper.domain.RegionTestSamples.*;
import static org.assertj.core.api.Assertions.assertThat;

import com.waste.helper.web.rest.TestUtil;
import java.util.HashSet;
import java.util.Set;
import org.junit.jupiter.api.Test;

class RegionTest {

    @Test
    void equalsVerifier() throws Exception {
        TestUtil.equalsVerifier(Region.class);
        Region region1 = getRegionSample1();
        Region region2 = new Region();
        assertThat(region1).isNotEqualTo(region2);

        region2.setId(region1.getId());
        assertThat(region1).isEqualTo(region2);

        region2 = getRegionSample2();
        assertThat(region1).isNotEqualTo(region2);
    }

    @Test
    void disposalGuidesTest() {
        Region region = getRegionRandomSampleGenerator();
        DisposalGuide disposalGuideBack = getDisposalGuideRandomSampleGenerator();

        region.addDisposalGuides(disposalGuideBack);
        assertThat(region.getDisposalGuides()).containsOnly(disposalGuideBack);
        assertThat(disposalGuideBack.getRegion()).isEqualTo(region);

        region.removeDisposalGuides(disposalGuideBack);
        assertThat(region.getDisposalGuides()).doesNotContain(disposalGuideBack);
        assertThat(disposalGuideBack.getRegion()).isNull();

        region.disposalGuides(new HashSet<>(Set.of(disposalGuideBack)));
        assertThat(region.getDisposalGuides()).containsOnly(disposalGuideBack);
        assertThat(disposalGuideBack.getRegion()).isEqualTo(region);

        region.setDisposalGuides(new HashSet<>());
        assertThat(region.getDisposalGuides()).doesNotContain(disposalGuideBack);
        assertThat(disposalGuideBack.getRegion()).isNull();
    }

    @Test
    void favoriteRegionsTest() {
        Region region = getRegionRandomSampleGenerator();
        FavoriteRegion favoriteRegionBack = getFavoriteRegionRandomSampleGenerator();

        region.addFavoriteRegions(favoriteRegionBack);
        assertThat(region.getFavoriteRegions()).containsOnly(favoriteRegionBack);
        assertThat(favoriteRegionBack.getRegion()).isEqualTo(region);

        region.removeFavoriteRegions(favoriteRegionBack);
        assertThat(region.getFavoriteRegions()).doesNotContain(favoriteRegionBack);
        assertThat(favoriteRegionBack.getRegion()).isNull();

        region.favoriteRegions(new HashSet<>(Set.of(favoriteRegionBack)));
        assertThat(region.getFavoriteRegions()).containsOnly(favoriteRegionBack);
        assertThat(favoriteRegionBack.getRegion()).isEqualTo(region);

        region.setFavoriteRegions(new HashSet<>());
        assertThat(region.getFavoriteRegions()).doesNotContain(favoriteRegionBack);
        assertThat(favoriteRegionBack.getRegion()).isNull();
    }
}
