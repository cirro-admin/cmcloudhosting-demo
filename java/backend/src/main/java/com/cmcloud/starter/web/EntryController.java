package com.cmcloud.starter.web;

import com.cmcloud.starter.domain.Entry;
import com.cmcloud.starter.domain.EntryRepository;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * The write path, kept to the smallest thing that proves persistence:
 * add a row, see it listed, restart the service, see it still listed.
 */
@RestController
@RequestMapping("/api/entries")
public class EntryController {

    public record NewEntry(@NotBlank @Size(max = 200) String message) {
    }

    private final EntryRepository entries;

    public EntryController(EntryRepository entries) {
        this.entries = entries;
    }

    @GetMapping
    public List<Entry> list() {
        return entries.findAllByOrderByCreatedAtDescIdDesc();
    }

    @PostMapping
    public ResponseEntity<Entry> create(@Valid @RequestBody NewEntry body) {
        Entry saved = entries.save(new Entry(body.message().trim()));
        return ResponseEntity.status(201).body(saved);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!entries.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        entries.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
