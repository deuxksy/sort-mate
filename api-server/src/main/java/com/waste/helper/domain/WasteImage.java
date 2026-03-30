package com.waste.helper.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.io.Serial;
import java.io.Serializable;
import org.hibernate.annotations.Cache;
import org.hibernate.annotations.CacheConcurrencyStrategy;

/**
 * A WasteImage.
 */
@Entity
@Table(name = "waste_image")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@SuppressWarnings("common-java:DuplicatedBlocks")
public class WasteImage implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "sequenceGenerator")
    @SequenceGenerator(name = "sequenceGenerator")
    @Column(name = "id")
    private Long id;

    @Column(name = "original_url")
    private String originalUrl;

    @Column(name = "thumbnail_url")
    private String thumbnailUrl;

    @ManyToOne(fetch = FetchType.LAZY)
    @JsonIgnoreProperties(value = { "user", "wasteImages", "feedbacks" }, allowSetters = true)
    private WasteClassification wasteClassification;

    // jhipster-needle-entity-add-field - JHipster will add fields here

    public Long getId() {
        return this.id;
    }

    public WasteImage id(Long id) {
        this.setId(id);
        return this;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getOriginalUrl() {
        return this.originalUrl;
    }

    public WasteImage originalUrl(String originalUrl) {
        this.setOriginalUrl(originalUrl);
        return this;
    }

    public void setOriginalUrl(String originalUrl) {
        this.originalUrl = originalUrl;
    }

    public String getThumbnailUrl() {
        return this.thumbnailUrl;
    }

    public WasteImage thumbnailUrl(String thumbnailUrl) {
        this.setThumbnailUrl(thumbnailUrl);
        return this;
    }

    public void setThumbnailUrl(String thumbnailUrl) {
        this.thumbnailUrl = thumbnailUrl;
    }

    public WasteClassification getWasteClassification() {
        return this.wasteClassification;
    }

    public void setWasteClassification(WasteClassification wasteClassification) {
        this.wasteClassification = wasteClassification;
    }

    public WasteImage wasteClassification(WasteClassification wasteClassification) {
        this.setWasteClassification(wasteClassification);
        return this;
    }

    // jhipster-needle-entity-add-getters-setters - JHipster will add getters and setters here

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof WasteImage)) {
            return false;
        }
        return getId() != null && getId().equals(((WasteImage) o).getId());
    }

    @Override
    public int hashCode() {
        // see https://vladmihalcea.com/how-to-implement-equals-and-hashcode-using-the-jpa-entity-identifier/
        return getClass().hashCode();
    }

    // prettier-ignore
    @Override
    public String toString() {
        return "WasteImage{" +
            "id=" + getId() +
            ", originalUrl='" + getOriginalUrl() + "'" +
            ", thumbnailUrl='" + getThumbnailUrl() + "'" +
            "}";
    }
}
