package com.waste.helper.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.io.Serial;
import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;
import org.hibernate.annotations.Cache;
import org.hibernate.annotations.CacheConcurrencyStrategy;

/**
 * A Region.
 */
@Entity
@Table(name = "region")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@SuppressWarnings("common-java:DuplicatedBlocks")
public class Region implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "sequenceGenerator")
    @SequenceGenerator(name = "sequenceGenerator")
    @Column(name = "id")
    private Long id;

    @Column(name = "sido")
    private String sido;

    @Column(name = "sigungu")
    private String sigungu;

    @Column(name = "emd_name")
    private String emdName;

    @Column(name = "emd_code", unique = true)
    private String emdCode;

    @OneToMany(fetch = FetchType.LAZY, mappedBy = "region")
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    @JsonIgnoreProperties(value = { "region" }, allowSetters = true)
    private Set<DisposalGuide> disposalGuides = new HashSet<>();

    @OneToMany(fetch = FetchType.LAZY, mappedBy = "region")
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    @JsonIgnoreProperties(value = { "user", "region" }, allowSetters = true)
    private Set<FavoriteRegion> favoriteRegions = new HashSet<>();

    // jhipster-needle-entity-add-field - JHipster will add fields here

    public Long getId() {
        return this.id;
    }

    public Region id(Long id) {
        this.setId(id);
        return this;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSido() {
        return this.sido;
    }

    public Region sido(String sido) {
        this.setSido(sido);
        return this;
    }

    public void setSido(String sido) {
        this.sido = sido;
    }

    public String getSigungu() {
        return this.sigungu;
    }

    public Region sigungu(String sigungu) {
        this.setSigungu(sigungu);
        return this;
    }

    public void setSigungu(String sigungu) {
        this.sigungu = sigungu;
    }

    public String getEmdName() {
        return this.emdName;
    }

    public Region emdName(String emdName) {
        this.setEmdName(emdName);
        return this;
    }

    public void setEmdName(String emdName) {
        this.emdName = emdName;
    }

    public String getEmdCode() {
        return this.emdCode;
    }

    public Region emdCode(String emdCode) {
        this.setEmdCode(emdCode);
        return this;
    }

    public void setEmdCode(String emdCode) {
        this.emdCode = emdCode;
    }

    public Set<DisposalGuide> getDisposalGuides() {
        return this.disposalGuides;
    }

    public void setDisposalGuides(Set<DisposalGuide> disposalGuides) {
        if (this.disposalGuides != null) {
            this.disposalGuides.forEach(i -> i.setRegion(null));
        }
        if (disposalGuides != null) {
            disposalGuides.forEach(i -> i.setRegion(this));
        }
        this.disposalGuides = disposalGuides;
    }

    public Region disposalGuides(Set<DisposalGuide> disposalGuides) {
        this.setDisposalGuides(disposalGuides);
        return this;
    }

    public Region addDisposalGuides(DisposalGuide disposalGuide) {
        this.disposalGuides.add(disposalGuide);
        disposalGuide.setRegion(this);
        return this;
    }

    public Region removeDisposalGuides(DisposalGuide disposalGuide) {
        this.disposalGuides.remove(disposalGuide);
        disposalGuide.setRegion(null);
        return this;
    }

    public Set<FavoriteRegion> getFavoriteRegions() {
        return this.favoriteRegions;
    }

    public void setFavoriteRegions(Set<FavoriteRegion> favoriteRegions) {
        if (this.favoriteRegions != null) {
            this.favoriteRegions.forEach(i -> i.setRegion(null));
        }
        if (favoriteRegions != null) {
            favoriteRegions.forEach(i -> i.setRegion(this));
        }
        this.favoriteRegions = favoriteRegions;
    }

    public Region favoriteRegions(Set<FavoriteRegion> favoriteRegions) {
        this.setFavoriteRegions(favoriteRegions);
        return this;
    }

    public Region addFavoriteRegions(FavoriteRegion favoriteRegion) {
        this.favoriteRegions.add(favoriteRegion);
        favoriteRegion.setRegion(this);
        return this;
    }

    public Region removeFavoriteRegions(FavoriteRegion favoriteRegion) {
        this.favoriteRegions.remove(favoriteRegion);
        favoriteRegion.setRegion(null);
        return this;
    }

    // jhipster-needle-entity-add-getters-setters - JHipster will add getters and setters here

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Region)) {
            return false;
        }
        return getId() != null && getId().equals(((Region) o).getId());
    }

    @Override
    public int hashCode() {
        // see https://vladmihalcea.com/how-to-implement-equals-and-hashcode-using-the-jpa-entity-identifier/
        return getClass().hashCode();
    }

    // prettier-ignore
    @Override
    public String toString() {
        return "Region{" +
            "id=" + getId() +
            ", sido='" + getSido() + "'" +
            ", sigungu='" + getSigungu() + "'" +
            ", emdName='" + getEmdName() + "'" +
            ", emdCode='" + getEmdCode() + "'" +
            "}";
    }
}
