package com.waste.helper.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.waste.helper.domain.enumeration.Source;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.io.Serial;
import java.io.Serializable;
import org.hibernate.annotations.Cache;
import org.hibernate.annotations.CacheConcurrencyStrategy;

/**
 * A DisposalGuide.
 */
@Entity
@Table(name = "disposal_guide")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@SuppressWarnings("common-java:DuplicatedBlocks")
public class DisposalGuide implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "sequenceGenerator")
    @SequenceGenerator(name = "sequenceGenerator")
    @Column(name = "id")
    private Long id;

    @NotNull
    @Column(name = "waste_type", nullable = false)
    private String wasteType;

    @Lob
    @Column(name = "disposal_method", nullable = false)
    private String disposalMethod;

    @Enumerated(EnumType.STRING)
    @Column(name = "source")
    private Source source;

    @ManyToOne(fetch = FetchType.LAZY)
    @JsonIgnoreProperties(value = { "disposalGuides", "favoriteRegions" }, allowSetters = true)
    private Region region;

    // jhipster-needle-entity-add-field - JHipster will add fields here

    public Long getId() {
        return this.id;
    }

    public DisposalGuide id(Long id) {
        this.setId(id);
        return this;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getWasteType() {
        return this.wasteType;
    }

    public DisposalGuide wasteType(String wasteType) {
        this.setWasteType(wasteType);
        return this;
    }

    public void setWasteType(String wasteType) {
        this.wasteType = wasteType;
    }

    public String getDisposalMethod() {
        return this.disposalMethod;
    }

    public DisposalGuide disposalMethod(String disposalMethod) {
        this.setDisposalMethod(disposalMethod);
        return this;
    }

    public void setDisposalMethod(String disposalMethod) {
        this.disposalMethod = disposalMethod;
    }

    public Source getSource() {
        return this.source;
    }

    public DisposalGuide source(Source source) {
        this.setSource(source);
        return this;
    }

    public void setSource(Source source) {
        this.source = source;
    }

    public Region getRegion() {
        return this.region;
    }

    public void setRegion(Region region) {
        this.region = region;
    }

    public DisposalGuide region(Region region) {
        this.setRegion(region);
        return this;
    }

    // jhipster-needle-entity-add-getters-setters - JHipster will add getters and setters here

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof DisposalGuide)) {
            return false;
        }
        return getId() != null && getId().equals(((DisposalGuide) o).getId());
    }

    @Override
    public int hashCode() {
        // see https://vladmihalcea.com/how-to-implement-equals-and-hashcode-using-the-jpa-entity-identifier/
        return getClass().hashCode();
    }

    // prettier-ignore
    @Override
    public String toString() {
        return "DisposalGuide{" +
            "id=" + getId() +
            ", wasteType='" + getWasteType() + "'" +
            ", disposalMethod='" + getDisposalMethod() + "'" +
            ", source='" + getSource() + "'" +
            "}";
    }
}
